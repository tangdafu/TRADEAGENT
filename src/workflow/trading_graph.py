"""
交易智能体 LangGraph 工作流
使用 LangGraph 实现并行数据采集和状态管理
"""
from typing import TypedDict, Optional, Dict, Any, List, Annotated
from langgraph.graph import StateGraph, END
from loguru import logger
import operator

from src.data_collectors.funding_rate import FundingRateCollector
from src.data_collectors.kline_volume import KlineVolumeCollector
from src.data_collectors.liquidation import LiquidationCollector
from src.data_collectors.news_sentiment import NewsSentimentCollector
from src.analyzers.factor_analyzer import FactorAnalyzer
from src.analyzers.market_signal_detector import MarketSignalDetector
from src.agent.trading_agent import TradingAgent


class TradingState(TypedDict):
    """交易分析状态"""
    symbol: str
    verbose: bool

    # 数据采集结果
    funding_rate: Optional[Dict[str, Any]]
    kline_volume: Optional[Dict[str, Any]]
    liquidation: Optional[Dict[str, Any]]
    news_sentiment: Optional[Dict[str, Any]]

    # 行情预判结果
    has_trading_opportunity: Optional[bool]
    signal_summary: Optional[str]

    # 处理结果
    formatted_data: Optional[str]
    analysis_result: Optional[str]

    # 错误追踪 - 使用 Annotated 支持并行更新
    errors: Annotated[List[str], operator.add]


# ============ 数据采集节点 ============

def collect_funding_rate_node(state: TradingState) -> Dict[str, Any]:
    """采集资金费率数据节点"""
    logger.info("节点: 采集资金费率数据")
    try:
        collector = FundingRateCollector()
        data = collector.collect(state["symbol"])

        # 打印关键决策信息
        if data:
            logger.info(f"【资金费率决策信息】")
            logger.info(f"  当前费率: {data.get('current_rate', 'N/A'):.4%}")
            logger.info(f"  24h平均: {data.get('avg_rate_24h', 'N/A'):.4%}")
            logger.info(f"  趋势: {data.get('trend', 'N/A')}")
            logger.info(f"  是否极端: {data.get('is_extreme', False)}")
            logger.info(f"  信号: {data.get('signal', 'N/A')}")

        logger.info("✓ 资金费率数据采集完成")
        return {"funding_rate": data, "errors": []}
    except Exception as e:
        error_msg = f"资金费率采集失败: {str(e)}"
        logger.error(error_msg)
        return {"funding_rate": None, "errors": [error_msg]}


def collect_kline_node(state: TradingState) -> Dict[str, Any]:
    """采集K线数据节点"""
    logger.info("节点: 采集K线数据")
    try:
        collector = KlineVolumeCollector()
        data = collector.collect(state["symbol"])

        # 打印关键决策信息
        if data:
            logger.info(f"【K线数据决策信息】")
            logger.info(f"  当前价格: {data.get('current_price', 'N/A')}")
            price_change_pct = data.get('price_change_pct', 0)
            if isinstance(price_change_pct, (int, float)):
                logger.info(f"  24h涨跌幅: {price_change_pct:.2f}%")
            else:
                logger.info(f"  24h涨跌幅: {price_change_pct}")
            logger.info(f"  价格趋势: {data.get('price_trend', 'N/A')}")
            logger.info(f"  成交量趋势: {data.get('volume_trend', 'N/A')}")
            logger.info(f"  成交量信号: {data.get('volume_signal', 'N/A')}")

        logger.info("✓ K线数据采集完成")
        return {"kline_volume": data, "errors": []}
    except Exception as e:
        error_msg = f"K线数据采集失败: {str(e)}"
        logger.error(error_msg)
        return {"kline_volume": None, "errors": [error_msg]}


def collect_liquidation_node(state: TradingState) -> Dict[str, Any]:
    """采集市场压力数据节点"""
    logger.info("节点: 采集市场压力数据")
    try:
        collector = LiquidationCollector()
        data = collector.collect(state["symbol"])

        # 打印关键决策信息
        if data and data.get('data_available'):
            logger.info(f"【市场压力数据决策信息】")
            logger.info(f"  持仓量: {data.get('open_interest', 'N/A')}")
            logger.info(f"  多空比: {data.get('long_short_ratio', 'N/A')}")
            logger.info(f"  多头占比: {data.get('long_account_pct', 'N/A'):.1f}%")
            logger.info(f"  空头占比: {data.get('short_account_pct', 'N/A'):.1f}%")
            logger.info(f"  买卖比: {data.get('buy_sell_ratio', 'N/A')}")
            logger.info(f"  风险等级: {data.get('risk_level', 'N/A')}")
            logger.info(f"  信号: {data.get('signal', 'N/A')}")
        else:
            logger.info(f"【市场压力数据决策信息】无可用数据")

        logger.info("✓ 市场压力数据采集完成")
        return {"liquidation": data, "errors": []}
    except Exception as e:
        error_msg = f"市场压力数据采集失败: {str(e)}"
        logger.error(error_msg)
        return {"liquidation": None, "errors": [error_msg]}


def collect_news_node(state: TradingState) -> Dict[str, Any]:
    """采集消息面数据节点"""
    logger.info("节点: 采集消息面数据")
    try:
        collector = NewsSentimentCollector()
        data = collector.collect(state["symbol"])

        # 打印关键决策信息
        if data and data.get('data_available'):
            logger.info(f"【消息面数据决策信息】")

            # 打印加密货币新闻
            crypto_news = data.get('crypto_news', {})
            news_list = crypto_news.get('news_list', [])
            logger.info(f"  加密货币新闻: {len(news_list)} 条")
            if news_list:
                logger.info(f"  最新新闻标题:")
                for i, news in enumerate(news_list[:3], 1):  # 只显示前3条
                    title = news.get('title', 'N/A')
                    sentiment = news.get('sentiment', 'N/A')
                    logger.info(f"    {i}. [{sentiment}] {title[:80]}{'...' if len(title) > 80 else ''}")

            # 打印社交媒体情绪
            logger.info(f"  社交媒体情绪: {data.get('social_sentiment', {}).get('sentiment', 'N/A')}")

            # 打印宏观新闻
            macro_news = data.get('macro_news', {})
            macro_list = macro_news.get('news_list', [])
            logger.info(f"  宏观新闻: {len(macro_list)} 条")
            if macro_list:
                logger.info(f"  最新宏观新闻:")
                for i, news in enumerate(macro_list[:2], 1):  # 只显示前2条
                    title = news.get('title', 'N/A')
                    logger.info(f"    {i}. {title[:80]}{'...' if len(title) > 80 else ''}")

            # 打印整体情绪
            overall = data.get('overall_sentiment', {})
            logger.info(f"  整体情绪: {overall.get('sentiment', 'N/A')} (得分: {overall.get('score', 0):.2f})")
            logger.info(f"  信号: {overall.get('signal', 'N/A')}")
        else:
            logger.info(f"【消息面数据决策信息】无可用数据（需要配置API密钥）")

        logger.info("✓ 消息面数据采集完成")
        return {"news_sentiment": data, "errors": []}
    except Exception as e:
        error_msg = f"消息面数据采集失败: {str(e)}"
        logger.error(error_msg)
        return {"news_sentiment": None, "errors": [error_msg]}


# ============ 数据处理节点 ============

def market_signal_detection_node(state: TradingState) -> Dict[str, Any]:
    """行情预判节点"""
    logger.info("节点: 行情预判")
    try:
        # 检查是否有关键数据
        if not state["funding_rate"] or not state["kline_volume"]:
            logger.warning("缺少关键数据，跳过行情预判")
            return {
                "has_trading_opportunity": True,
                "signal_summary": "数据不足，默认进行AI分析",
                "errors": [],
            }

        # 创建信号检测器
        detector = MarketSignalDetector()

        # 检测交易机会
        has_opportunity, signals, signal_details = detector.detect_trading_opportunity(
            funding_rate=state["funding_rate"],
            kline_volume=state["kline_volume"],
            liquidation=state["liquidation"] or {},
            news_sentiment=state["news_sentiment"] or {},
        )

        # 格式化信号摘要
        signal_summary = detector.format_signal_summary(
            has_opportunity, signals, signal_details
        )

        # 打印预判结果
        logger.info("=" * 70)
        logger.info("【行情预判结果】")
        logger.info(f"  是否有交易机会: {'是' if has_opportunity else '否'}")
        logger.info(f"  触发信号数: {len(signals)}")
        if signals:
            logger.info(f"  触发信号:")
            for signal in signals:
                logger.info(f"    • {signal}")
        logger.info("=" * 70)

        if not has_opportunity:
            logger.info("⏭️  未检测到明显交易机会，跳过AI分析")
        else:
            logger.info("✅ 检测到交易机会，将进行AI分析")

        return {
            "has_trading_opportunity": has_opportunity,
            "signal_summary": signal_summary,
            "errors": [],
        }
    except Exception as e:
        error_msg = f"行情预判失败: {str(e)}"
        logger.error(error_msg)
        # 预判失败时，默认进行AI分析
        return {
            "has_trading_opportunity": True,
            "signal_summary": f"预判失败: {str(e)}",
            "errors": [error_msg],
        }


def format_data_node(state: TradingState) -> Dict[str, Any]:
    """格式化数据节点"""
    logger.info("节点: 格式化数据")
    try:
        # 检查是否有关键数据
        if not state["funding_rate"] or not state["kline_volume"]:
            raise ValueError("缺少关键数据（资金费率或K线数据）")

        # 构建分析数据
        analysis_data = {
            "symbol": state["symbol"],
            "funding_rate": state["funding_rate"],
            "kline_volume": state["kline_volume"],
            "liquidation": state["liquidation"] or {},
            "news_sentiment": state["news_sentiment"] or {},
        }

        # 格式化为LLM可读文本
        analyzer = FactorAnalyzer()
        formatted_text = analyzer.format_for_llm(analysis_data)

        # 打印格式化摘要
        logger.info(f"【数据格式化完成】")
        logger.info(f"  交易对: {state['symbol']}")
        logger.info(f"  数据源: 资金费率✓ K线✓ 市场压力{'✓' if state['liquidation'] else '✗'} 消息面{'✓' if state['news_sentiment'] else '✗'}")
        logger.info(f"  格式化文本长度: {len(formatted_text)} 字符")

        if state["verbose"]:
            logger.info("格式化数据预览:")
            logger.info(formatted_text[:500] + "...")

        logger.info("✓ 数据格式化完成")
        return {"formatted_data": formatted_text, "errors": []}
    except Exception as e:
        error_msg = f"数据格式化失败: {str(e)}"
        logger.error(error_msg)
        return {"formatted_data": None, "errors": [error_msg]}


def ai_analysis_node(state: TradingState) -> Dict[str, Any]:
    """AI分析节点"""
    logger.info("节点: AI分析")
    try:
        # 检查是否有交易机会
        if not state.get("has_trading_opportunity", True):
            logger.info("⏭️  无交易机会，跳过AI分析")
            return {
                "analysis_result": f"【无需分析】\n{state.get('signal_summary', '未检测到明显交易机会')}",
                "errors": [],
            }

        if not state["formatted_data"]:
            raise ValueError("没有可用的格式化数据")

        agent = TradingAgent()
        result = agent.analyze(state["formatted_data"])

        # 打印AI分析决策摘要
        logger.info(f"【AI分析决策完成】")
        logger.info(f"  分析结果长度: {len(result)} 字符")

        # 提取关键决策信息（如果结果中包含）
        if result:
            # 记录完整的AI分析结果到日志文件
            logger.info("=" * 70)
            logger.info("【完整AI分析结果】")
            logger.info(result)
            logger.info("=" * 70)

        logger.info("✓ AI分析完成")
        return {"analysis_result": result, "errors": []}
    except Exception as e:
        error_msg = f"AI分析失败: {str(e)}"
        logger.error(error_msg)
        return {"analysis_result": None, "errors": [error_msg]}


# ============ 构建工作流图 ============

def create_trading_graph():
    """创建交易分析工作流图"""

    # 创建状态图
    workflow = StateGraph(TradingState)

    # 添加数据采集节点（这些节点可以并行执行）
    workflow.add_node("collect_funding_rate", collect_funding_rate_node)
    workflow.add_node("collect_kline", collect_kline_node)
    workflow.add_node("collect_liquidation", collect_liquidation_node)
    workflow.add_node("collect_news", collect_news_node)

    # 添加数据处理节点
    workflow.add_node("market_signal_detection", market_signal_detection_node)
    workflow.add_node("format_data", format_data_node)
    workflow.add_node("ai_analysis", ai_analysis_node)

    # 设置入口点 - 从4个数据采集节点开始（并行执行）
    workflow.set_entry_point("collect_funding_rate")
    workflow.set_entry_point("collect_kline")
    workflow.set_entry_point("collect_liquidation")
    workflow.set_entry_point("collect_news")

    # 所有数据采集完成后，进入行情预判节点
    workflow.add_edge("collect_funding_rate", "market_signal_detection")
    workflow.add_edge("collect_kline", "market_signal_detection")
    workflow.add_edge("collect_liquidation", "market_signal_detection")
    workflow.add_edge("collect_news", "market_signal_detection")

    # 行情预判完成后，进入格式化节点
    workflow.add_edge("market_signal_detection", "format_data")

    # 格式化完成后，进入AI分析
    workflow.add_edge("format_data", "ai_analysis")

    # AI分析完成后，结束
    workflow.add_edge("ai_analysis", END)

    # 编译工作流
    app = workflow.compile()

    return app


def run_trading_analysis(symbol: str, verbose: bool = False) -> Dict[str, Any]:
    """
    运行交易分析工作流

    Args:
        symbol: 交易对符号 (如 BTCUSDT)
        verbose: 是否输出详细信息

    Returns:
        包含分析结果的字典
    """
    logger.info(f"启动 LangGraph 工作流分析: {symbol}")

    # 创建工作流
    app = create_trading_graph()

    # 生成并保存工作流图像
    try:
        from pathlib import Path
        graph_output_dir = Path("logs")
        graph_output_dir.mkdir(exist_ok=True)

        # 打印工作流结构（文本形式）
        logger.info("=" * 70)
        logger.info("【LangGraph 工作流结构】")
        logger.info("")
        logger.info("入口节点（并行执行）:")
        logger.info("  ├─ collect_funding_rate  (采集资金费率)")
        logger.info("  ├─ collect_kline         (采集K线数据)")
        logger.info("  ├─ collect_liquidation   (采集市场压力数据)")
        logger.info("  └─ collect_news          (采集消息面数据)")
        logger.info("")
        logger.info("数据处理节点:")
        logger.info("  ├─ market_signal_detection (行情预判)")
        logger.info("  ├─ format_data             (格式化数据)")
        logger.info("  └─ ai_analysis             (AI分析)")
        logger.info("")
        logger.info("工作流执行顺序:")
        logger.info("  [并行] 4个数据采集节点同时执行")
        logger.info("  ↓")
        logger.info("  [等待] 所有采集完成后进入行情预判")
        logger.info("  ↓")
        logger.info("  [串行] 行情预判 → 格式化数据 → AI分析 → 结束")
        logger.info("  注: 若无交易机会，AI分析将被跳过")
        logger.info("=" * 70)

        # 尝试生成 ASCII 图
        try:
            graph_ascii = app.get_graph().draw_ascii()
            logger.info("")
            logger.info("【LangGraph ASCII 图】")
            logger.info(graph_ascii)
            logger.info("=" * 70)
        except Exception as e:
            logger.debug(f"无法生成 ASCII 图: {e}")

        # 尝试生成 Mermaid 图
        try:
            mermaid_graph = app.get_graph().draw_mermaid()
            mermaid_file = graph_output_dir / "workflow_graph.mmd"
            with open(mermaid_file, "w", encoding="utf-8") as f:
                f.write(mermaid_graph)
            logger.info(f"工作流 Mermaid 图已保存到: {mermaid_file}")
        except Exception as e:
            logger.debug(f"无法生成 Mermaid 图: {e}")

    except Exception as e:
        logger.warning(f"无法生成工作流图: {e}")

    # 初始化状态
    initial_state: TradingState = {
        "symbol": symbol,
        "verbose": verbose,
        "funding_rate": None,
        "kline_volume": None,
        "liquidation": None,
        "news_sentiment": None,
        "has_trading_opportunity": None,
        "signal_summary": None,
        "formatted_data": None,
        "analysis_result": None,
        "errors": [],
    }

    # 执行工作流
    logger.info("开始执行工作流...")
    final_state = app.invoke(initial_state)

    # 检查错误
    if final_state["errors"]:
        logger.warning(f"工作流执行过程中出现 {len(final_state['errors'])} 个错误:")
        for error in final_state["errors"]:
            logger.warning(f"  - {error}")

    logger.info("工作流执行完成")

    return final_state
