from typing import Dict, Any
from loguru import logger
from src.data_collectors.funding_rate import FundingRateCollector
from src.data_collectors.kline_volume import KlineVolumeCollector
from src.data_collectors.liquidation import LiquidationCollector
from src.data_collectors.news_sentiment import NewsSentimentCollector


class FactorAnalyzer:
    """因素分析器 - 整合所有数据采集器"""

    def __init__(self):
        self.funding_rate_collector = FundingRateCollector()
        self.kline_volume_collector = KlineVolumeCollector()
        self.liquidation_collector = LiquidationCollector()
        self.news_sentiment_collector = NewsSentimentCollector()

    def analyze_all_factors(self, symbol: str) -> Dict[str, Any]:
        """采集并分析所有因素"""
        logger.info(f"开始分析所有因素: {symbol}")

        try:
            # 采集四个因素的数据
            funding_rate_data = self.funding_rate_collector.collect(symbol)
            kline_volume_data = self.kline_volume_collector.collect(symbol)
            liquidation_data = self.liquidation_collector.collect(symbol)
            news_sentiment_data = self.news_sentiment_collector.collect(symbol)

            return {
                "symbol": symbol,
                "funding_rate": funding_rate_data,
                "kline_volume": kline_volume_data,
                "liquidation": liquidation_data,
                "news_sentiment": news_sentiment_data,
            }
        except Exception as e:
            logger.error(f"分析因素失败: {str(e)}")
            raise

    def format_for_llm(self, analysis_data: Dict[str, Any]) -> str:
        """将分析数据格式化为LLM可读的文本"""
        symbol = analysis_data["symbol"]
        fr = analysis_data["funding_rate"]
        kv = analysis_data["kline_volume"]
        lq = analysis_data["liquidation"]
        ns = analysis_data["news_sentiment"]

        formatted_text = f"""
【交易对】{symbol}

【资金费率分析】
- 当前资金费率: {fr['current_rate']:.6f} ({fr['current_rate']*100:.4f}%)
- 24小时最高: {fr['max_rate_24h']:.6f}
- 24小时最低: {fr['min_rate_24h']:.6f}
- 24小时平均: {fr['avg_rate_24h']:.6f}
- 趋势: {fr['trend']}
- 是否极端: {'是' if fr['is_extreme'] else '否'}
- 信号: {fr['signal']}

【K线与成交量分析】
- 当前价格: ${kv['current_price']:.2f}
- 24小时最高: ${kv['highest_price_24h']:.2f}
- 24小时最低: ${kv['lowest_price_24h']:.2f}
- 价格变化: ${kv['price_change']:.2f} ({kv['price_change_pct']:.2f}%)
- 价格趋势: {kv['price_trend']}
- 支撑位: ${kv['support']:.2f}
- 阻力位: ${kv['resistance']:.2f}
- 成交量趋势: {kv['volume_trend']}
- 成交量信号: {kv['volume_signal']}

【市场压力分析】{'' if lq.get('data_available', True) else '（无法获取数据）'}
- 持仓量: {lq['open_interest']}
- 多空比: {lq['long_short_ratio']}
- 多头占比: {lq['long_account_pct']:.1f}%
- 空头占比: {lq['short_account_pct']:.1f}%
- 买卖比: {lq['buy_sell_ratio']}
- 主动买量: {lq['buy_volume']}
- 主动卖量: {lq['sell_volume']}
- 风险等级: {lq['risk_level']}
- 信号: {lq['signal']}

【消息面与情绪分析】{'' if ns.get('crypto_news', {}).get('data_available', True) else '（无法获取数据）'}
- 整体情绪: {ns['overall_sentiment']['sentiment']}
- 情绪得分: {ns['overall_sentiment']['score']:.2f}
- 信号: {ns['overall_sentiment']['signal']}

【加密货币新闻】
- 新闻数量: {ns['crypto_news']['news_count']}
- 正面新闻: {ns['crypto_news']['positive_count']}
- 负面新闻: {ns['crypto_news']['negative_count']}
- 中性新闻: {ns['crypto_news']['neutral_count']}
- 情绪得分: {ns['crypto_news']['sentiment_score']:.2f}

【社交媒体情绪】
- Twitter关注者: {ns['social_sentiment'].get('twitter_followers', 0):,}
- Reddit订阅者: {ns['social_sentiment'].get('reddit_subscribers', 0):,}
- 社交情绪: {ns['social_sentiment'].get('sentiment', 'neutral')}
"""

        # 添加最新新闻标题
        if ns['crypto_news']['news_list']:
            formatted_text += "\n【最新相关新闻】\n"
            for i, news in enumerate(ns['crypto_news']['news_list'][:3], 1):
                formatted_text += f"  {i}. [{news['sentiment']}] {news['title']}\n"

        # 添加宏观新闻
        if ns['macro_news']['news_list']:
            formatted_text += "\n【宏观财经新闻】\n"
            for i, news in enumerate(ns['macro_news']['news_list'][:2], 1):
                formatted_text += f"  {i}. {news['title']}\n"

        return formatted_text
