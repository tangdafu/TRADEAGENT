from typing import Dict, Any, List
from binance.client import Client
from loguru import logger
from .base import BaseCollector


class FundingRateCollector(BaseCollector):
    """资金费率采集器"""

    def __init__(self):
        super().__init__()
        self.client = Client()

    def collect(self, symbol: str) -> Dict[str, Any]:
        """采集资金费率数据"""
        logger.info(f"采集资金费率数据: {symbol}")

        def _fetch():
            # 获取当前资金费率
            current_rate = self.client.futures_funding_rate(symbol=symbol, limit=1)
            if not current_rate:
                raise ValueError("无法获取当前资金费率")

            current_rate_value = float(current_rate[0]["fundingRate"])

            # 获取历史资金费率（近24小时）
            history_rates = self.client.futures_funding_rate(symbol=symbol, limit=24)
            history_values = [float(r["fundingRate"]) for r in history_rates]

            # 计算统计信息
            max_rate = max(history_values)
            min_rate = min(history_values)
            avg_rate = sum(history_values) / len(history_values)

            # 判断极端情况
            extreme_threshold = 0.001  # ±0.1%
            is_extreme = (
                current_rate_value >= extreme_threshold
                or current_rate_value <= -extreme_threshold
            )

            # 判断趋势
            if len(history_values) >= 2:
                recent_avg = sum(history_values[-6:]) / 6  # 最近6个数据点
                older_avg = sum(history_values[:6]) / 6  # 最早6个数据点
                if recent_avg > older_avg:
                    trend = "上升"
                elif recent_avg < older_avg:
                    trend = "下降"
                else:
                    trend = "平稳"
            else:
                trend = "数据不足"

            # 生成信号
            if is_extreme:
                if current_rate_value > 0:
                    signal = "多头拥挤，短期易回调"
                else:
                    signal = "空头拥挤，短期易反弹"
            else:
                signal = "正常"

            return {
                "current_rate": current_rate_value,
                "max_rate_24h": max_rate,
                "min_rate_24h": min_rate,
                "avg_rate_24h": avg_rate,
                "trend": trend,
                "is_extreme": is_extreme,
                "signal": signal,
                "history": history_values,
            }

        return self._retry_on_error(_fetch)
