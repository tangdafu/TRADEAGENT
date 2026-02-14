from typing import Dict, Any
from binance.client import Client
from loguru import logger
from .base import BaseCollector


class KlineVolumeCollector(BaseCollector):
    """K线和成交量采集器"""

    def __init__(self):
        super().__init__()
        self.client = Client()

    def collect(self, symbol: str) -> Dict[str, Any]:
        """采集K线和成交量数据"""
        logger.info(f"采集K线和成交量数据: {symbol}")

        def _fetch():
            # 获取近24小时K线数据（1小时周期）
            klines = self.client.futures_klines(
                symbol=symbol, interval="1h", limit=24
            )

            if not klines:
                raise ValueError("无法获取K线数据")

            # 解析K线数据
            prices = []
            volumes = []
            times = []

            for kline in klines:
                open_price = float(kline[1])
                high_price = float(kline[2])
                low_price = float(kline[3])
                close_price = float(kline[4])
                volume = float(kline[7])  # 成交额

                prices.append(close_price)
                volumes.append(volume)
                times.append(kline[0])

            # 计算价格统计
            current_price = prices[-1]
            highest_price = max(prices)
            lowest_price = min(prices)
            price_change = prices[-1] - prices[0]
            price_change_pct = (price_change / prices[0]) * 100

            # 计算成交量统计
            avg_volume = sum(volumes) / len(volumes)
            current_volume = volumes[-1]
            volume_trend = "放量" if current_volume > avg_volume else "缩量"

            # 识别支撑阻力位
            support = lowest_price
            resistance = highest_price

            # 判断价格趋势
            if price_change_pct > 1:
                price_trend = "上升"
            elif price_change_pct < -1:
                price_trend = "下降"
            else:
                price_trend = "震荡"

            # 生成成交量信号
            if volume_trend == "放量":
                if price_trend == "上升":
                    volume_signal = "放量上涨，趋势延续"
                elif price_trend == "下降":
                    volume_signal = "放量下跌，恐慌延续"
                else:
                    volume_signal = "放量震荡，方向不明"
            else:
                if price_trend == "上升":
                    volume_signal = "缩量上涨，易回落"
                elif price_trend == "下降":
                    volume_signal = "缩量下跌，跌势放缓"
                else:
                    volume_signal = "缩量震荡，观望"

            return {
                "current_price": current_price,
                "highest_price_24h": highest_price,
                "lowest_price_24h": lowest_price,
                "price_change": price_change,
                "price_change_pct": price_change_pct,
                "price_trend": price_trend,
                "support": support,
                "resistance": resistance,
                "avg_volume": avg_volume,
                "current_volume": current_volume,
                "volume_trend": volume_trend,
                "volume_signal": volume_signal,
                "prices": prices,
                "volumes": volumes,
            }

        return self._retry_on_error(_fetch)
