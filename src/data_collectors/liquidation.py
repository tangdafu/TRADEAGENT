from typing import Dict, Any
import requests
from loguru import logger
from .base import BaseCollector


class LiquidationCollector(BaseCollector):
    """市场压力数据采集器（替代爆仓数据）

    注意：Binance 爆仓数据 API 已停止维护，改用以下替代指标：
    1. 持仓量 (Open Interest) - 反映市场参与度
    2. 多空比 (Long/Short Ratio) - 反映市场情绪
    3. 主动买卖量 (Taker Buy/Sell Volume) - 反映市场压力
    """

    def __init__(self):
        super().__init__()
        self.base_url = "https://fapi.binance.com"
        logger.info("初始化市场压力数据采集器（使用公开API，无需密钥）")

    def collect(self, symbol: str) -> Dict[str, Any]:
        """采集市场压力数据"""
        logger.info(f"采集市场压力数据: {symbol}")

        def _fetch():
            try:
                # 1. 获取持仓量
                oi_data = self._get_open_interest(symbol)

                # 2. 获取多空比
                long_short_ratio = self._get_long_short_ratio(symbol)

                # 3. 获取主动买卖量
                taker_volume = self._get_taker_volume(symbol)

                # 分析市场压力
                signal, risk_level = self._analyze_market_pressure(
                    long_short_ratio, taker_volume
                )

                return {
                    "open_interest": oi_data.get("openInterest", "0"),
                    "long_short_ratio": long_short_ratio.get("longShortRatio", "0"),
                    "long_account_pct": float(long_short_ratio.get("longAccount", "0")) * 100,
                    "short_account_pct": float(long_short_ratio.get("shortAccount", "0")) * 100,
                    "buy_sell_ratio": taker_volume.get("buySellRatio", "0"),
                    "buy_volume": taker_volume.get("buyVol", "0"),
                    "sell_volume": taker_volume.get("sellVol", "0"),
                    "risk_level": risk_level,
                    "signal": signal,
                    "data_available": True,
                }

            except Exception as e:
                logger.error(f"获取市场压力数据失败: {str(e)}")
                return {
                    "open_interest": "0",
                    "long_short_ratio": "0",
                    "long_account_pct": 0.0,
                    "short_account_pct": 0.0,
                    "buy_sell_ratio": "0",
                    "buy_volume": "0",
                    "sell_volume": "0",
                    "risk_level": "未知",
                    "signal": "无法获取数据",
                    "data_available": False,
                }

        return self._retry_on_error(_fetch)

    def _get_open_interest(self, symbol: str) -> Dict[str, Any]:
        """获取持仓量"""
        url = f"{self.base_url}/fapi/v1/openInterest"
        response = requests.get(url, params={"symbol": symbol}, timeout=10)
        response.raise_for_status()
        return response.json()

    def _get_long_short_ratio(self, symbol: str) -> Dict[str, Any]:
        """获取多空比（最新数据）"""
        url = f"{self.base_url}/futures/data/globalLongShortAccountRatio"
        params = {
            "symbol": symbol,
            "period": "5m",
            "limit": 1
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data[0] if data else {}

    def _get_taker_volume(self, symbol: str) -> Dict[str, Any]:
        """获取主动买卖量（最新数据）"""
        url = f"{self.base_url}/futures/data/takerlongshortRatio"
        params = {
            "symbol": symbol,
            "period": "5m",
            "limit": 1
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data[0] if data else {}

    def _analyze_market_pressure(
        self, long_short_ratio: Dict[str, Any], taker_volume: Dict[str, Any]
    ) -> tuple[str, str]:
        """分析市场压力，生成信号"""
        try:
            ls_ratio = float(long_short_ratio.get("longShortRatio", "1"))
            long_pct = float(long_short_ratio.get("longAccount", "0.5"))
            bs_ratio = float(taker_volume.get("buySellRatio", "1"))

            # 风险等级判断
            if ls_ratio > 2.5 or long_pct > 0.75:
                risk_level = "高风险"
                signal = "多头过度拥挤，警惕回调风险"
            elif ls_ratio < 0.5 or long_pct < 0.25:
                risk_level = "高风险"
                signal = "空头过度拥挤，警惕反弹风险"
            elif ls_ratio > 1.8 or long_pct > 0.65:
                risk_level = "中等风险"
                signal = "多头占优，注意获利回吐"
            elif ls_ratio < 0.7 or long_pct < 0.35:
                risk_level = "中等风险"
                signal = "空头占优，注意空头回补"
            else:
                risk_level = "低风险"
                signal = "多空相对平衡"

            # 结合买卖压力
            if bs_ratio > 1.2:
                signal += "，主动买盘强劲"
            elif bs_ratio < 0.8:
                signal += "，主动卖盘强劲"

            return signal, risk_level

        except Exception as e:
            logger.warning(f"分析市场压力失败: {str(e)}")
            return "数据异常", "未知"
