from typing import Dict, Any
from loguru import logger
from src.data_collectors.funding_rate import FundingRateCollector
from src.data_collectors.kline_volume import KlineVolumeCollector
from src.data_collectors.liquidation import LiquidationCollector


class FactorAnalyzer:
    """因素分析器 - 整合所有数据采集器"""

    def __init__(self):
        self.funding_rate_collector = FundingRateCollector()
        self.kline_volume_collector = KlineVolumeCollector()
        self.liquidation_collector = LiquidationCollector()

    def analyze_all_factors(self, symbol: str) -> Dict[str, Any]:
        """采集并分析所有因素"""
        logger.info(f"开始分析所有因素: {symbol}")

        try:
            # 采集三个因素的数据
            funding_rate_data = self.funding_rate_collector.collect(symbol)
            kline_volume_data = self.kline_volume_collector.collect(symbol)
            liquidation_data = self.liquidation_collector.collect(symbol)

            return {
                "symbol": symbol,
                "funding_rate": funding_rate_data,
                "kline_volume": kline_volume_data,
                "liquidation": liquidation_data,
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

【爆仓数据分析】{'（模拟数据）' if lq.get('is_mock', False) else ''}
- 总爆仓金额: ${lq['total_liquidation']:,.0f}
- 多单爆仓: ${lq['long_liquidation']:,.0f} ({lq['long_pct']:.1f}%)
- 空单爆仓: ${lq['short_liquidation']:,.0f} ({lq['short_pct']:.1f}%)
- 爆仓笔数: {lq['liquidation_count']}
- 大额爆仓笔数: {len(lq['large_liquidations'])}
- 信号: {lq['signal']}
"""

        if lq["large_liquidations"]:
            formatted_text += "\n【大额爆仓详情】\n"
            for i, liq in enumerate(lq["large_liquidations"][:5], 1):  # 只显示前5笔
                formatted_text += f"  {i}. {liq['side']}: ${liq['amount']:,.0f} @ ${liq['price']:.2f}\n"

        return formatted_text
