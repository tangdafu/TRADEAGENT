"""
市场信号检测器
根据多个技术指标判断是否存在交易机会，避免无效的AI分析调用
"""
from typing import Dict, Any, List, Tuple
from loguru import logger
from config.settings import settings


class MarketSignalDetector:
    """市场信号检测器 - 预判是否有交易机会"""

    def __init__(self):
        self.enabled = settings.MARKET_SIGNAL_DETECTION_ENABLED
        self.signals = []

    def detect_trading_opportunity(
        self,
        funding_rate: Dict[str, Any],
        kline_volume: Dict[str, Any],
        liquidation: Dict[str, Any],
        news_sentiment: Dict[str, Any],
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        检测是否存在交易机会

        Args:
            funding_rate: 资金费率数据
            kline_volume: K线和成交量数据
            liquidation: 爆仓数据
            news_sentiment: 消息面数据

        Returns:
            (是否有交易机会, 触发信号列表, 信号详情)
        """
        if not self.enabled:
            logger.info("行情预判功能已禁用，将进行AI分析")
            return True, ["预判功能已禁用"], {}

        self.signals = []
        signal_details = {}

        # 1. 检查资金费率信号
        funding_signal = self._check_funding_rate_signal(funding_rate)
        if funding_signal:
            self.signals.append(funding_signal["type"])
            signal_details["funding_rate"] = funding_signal

        # 2. 检查价格波动信号
        price_signal = self._check_price_volatility_signal(kline_volume)
        if price_signal:
            self.signals.append(price_signal["type"])
            signal_details["price_volatility"] = price_signal

        # 3. 检查成交量异常信号
        volume_signal = self._check_volume_anomaly_signal(kline_volume)
        if volume_signal:
            self.signals.append(volume_signal["type"])
            signal_details["volume_anomaly"] = volume_signal

        # 4. 检查爆仓信号
        liquidation_signal = self._check_liquidation_signal(liquidation)
        if liquidation_signal:
            self.signals.append(liquidation_signal["type"])
            signal_details["liquidation"] = liquidation_signal

        # 5. 检查消息面信号
        news_signal = self._check_news_sentiment_signal(news_sentiment)
        if news_signal:
            self.signals.append(news_signal["type"])
            signal_details["news_sentiment"] = news_signal

        # 判断是否有交易机会
        has_opportunity = len(self.signals) >= settings.MIN_SIGNAL_COUNT

        return has_opportunity, self.signals, signal_details

    def _check_funding_rate_signal(
        self, funding_rate: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查资金费率信号"""
        if not funding_rate:
            return None

        current_rate = funding_rate.get("current_rate", 0)
        is_extreme = funding_rate.get("is_extreme", False)
        trend = funding_rate.get("trend", "")

        # 极端资金费率（强信号）
        if is_extreme:
            if current_rate > settings.FUNDING_RATE_EXTREME_THRESHOLD:
                return {
                    "type": "资金费率极端做多",
                    "strength": "强",
                    "value": current_rate,
                    "description": f"资金费率达到 {current_rate:.4%}，多头过度拥挤，可能回调",
                }
            elif current_rate < -settings.FUNDING_RATE_EXTREME_THRESHOLD:
                return {
                    "type": "资金费率极端做空",
                    "strength": "强",
                    "value": current_rate,
                    "description": f"资金费率达到 {current_rate:.4%}，空头过度拥挤，可能反弹",
                }

        # 资金费率快速变化（中等信号）
        if abs(current_rate) > settings.FUNDING_RATE_CHANGE_THRESHOLD:
            if trend == "上升" and current_rate > 0:
                return {
                    "type": "资金费率快速上升",
                    "strength": "中",
                    "value": current_rate,
                    "description": f"资金费率快速上升至 {current_rate:.4%}，多头情绪升温",
                }
            elif trend == "下降" and current_rate < 0:
                return {
                    "type": "资金费率快速下降",
                    "strength": "中",
                    "value": current_rate,
                    "description": f"资金费率快速下降至 {current_rate:.4%}，空头情绪升温",
                }

        return None

    def _check_price_volatility_signal(
        self, kline_volume: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查价格波动信号"""
        if not kline_volume:
            return None

        price_change_pct = kline_volume.get("price_change_pct", 0)
        price_trend = kline_volume.get("price_trend", "")

        # 大幅波动（强信号）
        if abs(price_change_pct) >= settings.PRICE_CHANGE_THRESHOLD:
            if price_change_pct > 0:
                return {
                    "type": "价格大幅上涨",
                    "strength": "强",
                    "value": price_change_pct,
                    "description": f"24h涨幅 {price_change_pct:.2f}%，趋势：{price_trend}",
                }
            else:
                return {
                    "type": "价格大幅下跌",
                    "strength": "强",
                    "value": price_change_pct,
                    "description": f"24h跌幅 {price_change_pct:.2f}%，趋势：{price_trend}",
                }

        return None

    def _check_volume_anomaly_signal(
        self, kline_volume: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查成交量异常信号"""
        if not kline_volume:
            return None

        volume_trend = kline_volume.get("volume_trend", "")
        volume_signal = kline_volume.get("volume_signal", "")
        current_volume = kline_volume.get("current_volume", 0)
        avg_volume = kline_volume.get("avg_volume", 0)

        if avg_volume == 0:
            return None

        volume_ratio = current_volume / avg_volume

        # 成交量异常放大（中等信号）
        if volume_trend == "放量" and volume_ratio >= settings.VOLUME_SURGE_RATIO:
            return {
                "type": "成交量异常放大",
                "strength": "中",
                "value": volume_ratio,
                "description": f"成交量是均值的 {volume_ratio:.2f} 倍，信号：{volume_signal}",
            }

        return None

    def _check_liquidation_signal(
        self, liquidation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查市场压力信号（替代爆仓信号）"""
        if not liquidation or not liquidation.get("data_available"):
            return None

        risk_level = liquidation.get("risk_level", "")
        long_short_ratio = float(liquidation.get("long_short_ratio", "1"))
        long_pct = liquidation.get("long_account_pct", 50)
        buy_sell_ratio = float(liquidation.get("buy_sell_ratio", "1"))

        # 高风险市场压力（强信号）
        if risk_level == "高风险":
            if long_short_ratio > 2.5 or long_pct > 75:
                return {
                    "type": "多头过度拥挤",
                    "strength": "强",
                    "value": long_short_ratio,
                    "description": f"多空比 {long_short_ratio:.2f}，多头占比 {long_pct:.1f}%，警惕回调风险",
                }
            elif long_short_ratio < 0.5 or long_pct < 25:
                return {
                    "type": "空头过度拥挤",
                    "strength": "强",
                    "value": long_short_ratio,
                    "description": f"多空比 {long_short_ratio:.2f}，空头占比 {100-long_pct:.1f}%，警惕反弹风险",
                }

        # 中等风险市场压力（中等信号）
        elif risk_level == "中等风险":
            if buy_sell_ratio > 1.2:
                return {
                    "type": "主动买盘强劲",
                    "strength": "中",
                    "value": buy_sell_ratio,
                    "description": f"买卖比 {buy_sell_ratio:.2f}，主动买盘占优",
                }
            elif buy_sell_ratio < 0.8:
                return {
                    "type": "主动卖盘强劲",
                    "strength": "中",
                    "value": buy_sell_ratio,
                    "description": f"买卖比 {buy_sell_ratio:.2f}，主动卖盘占优",
                }

        return None

    def _check_news_sentiment_signal(
        self, news_sentiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查消息面信号"""
        if not news_sentiment or not news_sentiment.get("data_available"):
            return None

        overall_sentiment = news_sentiment.get("overall_sentiment", {})
        sentiment = overall_sentiment.get("sentiment", "")
        score = overall_sentiment.get("score", 0)

        # 消息面情绪极端（中等信号）
        if abs(score) >= settings.NEWS_SENTIMENT_THRESHOLD:
            if score > 0:
                return {
                    "type": "消息面极度乐观",
                    "strength": "中",
                    "value": score,
                    "description": f"消息面情绪得分 {score:.2f}，倾向：{sentiment}",
                }
            else:
                return {
                    "type": "消息面极度悲观",
                    "strength": "中",
                    "value": score,
                    "description": f"消息面情绪得分 {score:.2f}，倾向：{sentiment}",
                }

        return None

    def format_signal_summary(
        self, has_opportunity: bool, signals: List[str], signal_details: Dict[str, Any]
    ) -> str:
        """格式化信号摘要"""
        if not self.enabled:
            return "行情预判功能已禁用"

        if not has_opportunity:
            return f"未检测到明显交易机会（触发信号数：{len(signals)}/{settings.MIN_SIGNAL_COUNT}）"

        summary = f"检测到交易机会！触发 {len(signals)} 个信号：\n"
        for signal_type, details in signal_details.items():
            summary += f"  • [{details['strength']}] {details['type']}: {details['description']}\n"

        return summary.strip()
