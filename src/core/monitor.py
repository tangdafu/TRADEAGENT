"""
监控模块 - 业务逻辑层
负责单次分析的执行，不包含调度逻辑
"""
from datetime import datetime
from typing import List
from loguru import logger

from src.workflow import run_trading_analysis
from src.database import AnalysisRepository
from src.alerts import AlertManager
from src.analyzers.accuracy_tracker import AccuracyTracker


class TradingMonitor:
    """交易监控器 - 负责执行单次分析"""

    def __init__(self):
        """初始化监控器"""
        self.repo = AnalysisRepository()
        self.alert_manager = AlertManager()
        self.tracker = AccuracyTracker()
        self.analysis_count = 0

    def analyze_symbol(self, symbol: str, verbose: bool = False) -> bool:
        """
        分析单个交易对

        Args:
            symbol: 交易对
            verbose: 是否详细输出

        Returns:
            bool: 是否分析成功
        """
        self.analysis_count += 1

        logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始分析 {symbol} (第 {self.analysis_count} 次)")

        try:
            # 运行分析
            final_state = run_trading_analysis(symbol, verbose)

            if not final_state.get("analysis_result"):
                logger.warning(f"{symbol} 分析失败")
                return False

            # 保存到数据库
            analysis_result = final_state["analysis_result"]
            analysis_id = self.repo.save_analysis(symbol, final_state, analysis_result)
            logger.info(f"分析结果已保存，ID: {analysis_id}")

            # 无论有无交易机会，都打印市场数据
            self._log_market_data(symbol, final_state)

            # 检查是否有交易机会
            has_opportunity = final_state.get("has_trading_opportunity", False)

            if has_opportunity:
                # 使用repository的方法提取告警数据
                alert_data = self.repo.extract_alert_data(final_state)

                # 传递完整的AI分析文本
                self.alert_manager.send_alert(symbol, alert_data, analysis_result)
                logger.info(f"✅ 检测到交易机会！已发送告警")
            else:
                logger.info(f"⏭️  暂无交易机会")

            return True

        except Exception as e:
            logger.error(f"分析 {symbol} 时出错: {e}", exc_info=True)
            return False

    def _log_market_data(self, symbol: str, final_state: dict):
        """
        打印市场数据摘要（无交易机会时）

        Args:
            symbol: 交易对
            final_state: 工作流最终状态
        """
        logger.info("=" * 70)
        logger.info(f"【{symbol} 市场数据摘要】")

        # K线数据
        kline_data = final_state.get('kline_volume', {})
        if kline_data:
            current_price = kline_data.get('current_price')
            price_change = kline_data.get('price_change_pct')
            volume_change = kline_data.get('volume_change_pct')

            if current_price:
                logger.info(f"当前价格: ${current_price:,.2f}")
            if price_change is not None:
                direction = "📈" if price_change > 0 else "📉" if price_change < 0 else "➡️"
                logger.info(f"24h涨跌: {direction} {price_change:+.2f}%")
            if volume_change is not None:
                logger.info(f"成交量变化: {volume_change:+.2f}%")

        # 资金费率
        funding_data = final_state.get('funding_rate', {})
        if funding_data:
            current_rate = funding_data.get('current_rate')
            if current_rate is not None:
                sentiment = "多头" if current_rate > 0 else "空头" if current_rate < 0 else "中性"
                logger.info(f"资金费率: {current_rate:.4f}% ({sentiment})")

        # 市场压力
        liquidation_data = final_state.get('liquidation', {})
        if liquidation_data:
            total_liquidation = liquidation_data.get('total_liquidation_usd')
            if total_liquidation:
                logger.info(f"市场压力: ${total_liquidation:,.0f}")

        # 消息面数据
        news_data = final_state.get('news_sentiment', {})
        if news_data:
            overall_sentiment = news_data.get('overall_sentiment', {})
            if isinstance(overall_sentiment, dict):
                sentiment = overall_sentiment.get('sentiment')
                score = overall_sentiment.get('score')
                if sentiment:
                    logger.info(f"消息面情绪: {sentiment} (评分: {score:.2f})" if score is not None else f"消息面情绪: {sentiment}")

            # 如果有具体的新闻标题
            crypto_news = news_data.get('crypto_news', {})
            news_list = crypto_news.get('news', [])
            if news_list and len(news_list) > 0:
                logger.info(f"相关新闻数: {len(news_list)} 条")
                logger.info("最新消息:")
                for i, news in enumerate(news_list[:3], 1):  # 只显示前3条
                    title = news.get('title', '')
                    if title:
                        logger.info(f"  {i}. {title[:60]}...")

        # 触发的信号
        triggered_signals = final_state.get('triggered_signals', [])
        if triggered_signals:
            logger.info(f"触发信号: {', '.join(triggered_signals)}")
        else:
            logger.info("触发信号: 无")

        # 信号摘要
        signal_summary = final_state.get('signal_summary', '')
        if signal_summary:
            logger.info(f"信号摘要: {signal_summary}")

        logger.info("=" * 70)

    def update_signals(self, symbol: str, hours: int = 24) -> int:
        """
        更新信号表现

        Args:
            symbol: 交易对
            hours: 追踪小时数

        Returns:
            int: 更新的信号数量
        """
        logger.info(f"更新 {symbol} 的信号表现...")
        try:
            updated_count = self.tracker.update_signal_performance(symbol, hours=hours)
            logger.info(f"已更新 {symbol} 的信号表现，更新了 {updated_count} 条记录")
            return updated_count
        except Exception as e:
            logger.error(f"更新信号表现失败: {e}", exc_info=True)
            return 0

    def get_analysis_count(self) -> int:
        """获取分析次数"""
        return self.analysis_count


def run_monitor_mode(symbols: List[str], interval: int, verbose: bool = False):
    """
    运行监控模式（使用APScheduler）

    Args:
        symbols: 交易对列表
        interval: 监控间隔（分钟）
        verbose: 是否详细输出
    """
    from src.core.scheduler import TradingScheduler

    # 初始化监控器
    monitor = TradingMonitor()

    # 初始化调度器
    scheduler = TradingScheduler()

    # 显示启动信息
    logger.info("=" * 70)
    logger.info("启动监控模式")
    logger.info(f"监控币种: {', '.join(symbols)}")
    logger.info(f"监控间隔: {interval} 分钟")
    logger.info("自动保存: 开启")
    logger.info("自动更新信号: 每小时一次")
    logger.info(f"飞书告警: {'开启' if monitor.alert_manager.feishu_enabled else '关闭'}")
    logger.info("=" * 70)

    # 定义分析任务
    def analysis_job():
        """分析任务"""
        for symbol in symbols:
            monitor.analyze_symbol(symbol, verbose)

    # 定义信号更新任务
    def signal_update_job():
        """信号更新任务"""
        for symbol in symbols:
            monitor.update_signals(symbol, hours=24)

    # 添加分析任务（按指定间隔执行）
    scheduler.add_interval_job(
        func=analysis_job,
        minutes=interval,
        job_id="trading_analysis"
    )

    # 添加信号更新任务（每小时执行一次）
    scheduler.add_interval_job(
        func=signal_update_job,
        minutes=60,
        job_id="signal_update"
    )

    # 立即执行一次分析
    logger.info("执行首次分析...")
    analysis_job()

    # 启动调度器
    scheduler.start()

    # 调度器停止后显示统计
    logger.info(f"监控已停止，共完成 {monitor.get_analysis_count()} 次分析")
