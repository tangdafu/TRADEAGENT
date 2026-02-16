from typing import Dict, Any
from binance.client import Client
from loguru import logger
from .base import BaseCollector
from config.settings import settings


class LiquidationCollector(BaseCollector):
    """爆仓数据采集器"""

    def __init__(self):
        super().__init__()
        # 如果配置了API密钥，则使用认证客户端
        if settings.BINANCE_API_KEY and settings.BINANCE_API_SECRET:
            self.client = Client(
                api_key=settings.BINANCE_API_KEY,
                api_secret=settings.BINANCE_API_SECRET
            )
            logger.info("使用Binance API密钥初始化爆仓数据采集器")
        else:
            self.client = Client()
            logger.warning("未配置Binance API密钥，将使用模拟爆仓数据")

    def collect(self, symbol: str) -> Dict[str, Any]:
        """采集爆仓数据"""
        logger.info(f"采集爆仓数据: {symbol}")

        def _fetch():
            try:
                # 尝试获取爆仓数据（需要API密钥）
                liquidations = self.client.futures_liquidation_orders(symbol=symbol)
            except Exception as e:
                # 如果需要API密钥，返回模拟数据
                logger.warning(f"无法获取爆仓数据（需要API密钥），使用模拟数据: {str(e)}")

                # 获取当前价格用于生成合理的模拟数据
                try:
                    ticker = self.client.futures_ticker(symbol=symbol)
                    current_price = float(ticker['lastPrice'])
                except Exception:
                    # 如果无法获取价格，使用默认值
                    current_price = 50000.0 if 'BTC' in symbol else 2000.0

                # 返回基于当前价格的模拟爆仓数据
                return {
                    "total_liquidation": 250000,
                    "long_liquidation": 150000,
                    "short_liquidation": 100000,
                    "long_pct": 60.0,
                    "short_pct": 40.0,
                    "large_liquidations": [
                        {
                            "price": current_price * 0.98,  # 当前价格下方2%
                            "qty": 2.0,
                            "amount": 139000.0,
                            "side": "多单",
                        }
                    ],
                    "liquidation_count": 15,
                    "signal": "爆仓正常（模拟数据）",
                    "is_mock": True,
                }

            if not liquidations:
                return {
                    "total_liquidation": 0,
                    "long_liquidation": 0,
                    "short_liquidation": 0,
                    "long_pct": 0.0,
                    "short_pct": 0.0,
                    "large_liquidations": [],
                    "liquidation_count": 0,
                    "signal": "无大额爆仓",
                    "is_mock": False,
                }

            # 解析爆仓数据
            total_liquidation = 0
            long_liquidation = 0
            short_liquidation = 0
            large_liquidations = []
            liquidation_threshold = 100000  # 100,000 USDT

            for liq in liquidations:
                price = float(liq["price"])
                qty = float(liq["qty"])
                liquidation_amount = price * qty

                total_liquidation += liquidation_amount

                # 判断多空
                if liq["side"] == "SELL":  # 多单爆仓
                    long_liquidation += liquidation_amount
                else:  # 空单爆仓
                    short_liquidation += liquidation_amount

                # 记录大额爆仓
                if liquidation_amount >= liquidation_threshold:
                    large_liquidations.append(
                        {
                            "price": price,
                            "qty": qty,
                            "amount": liquidation_amount,
                            "side": "多单" if liq["side"] == "SELL" else "空单",
                        }
                    )

            # 计算占比
            if total_liquidation > 0:
                long_pct = (long_liquidation / total_liquidation) * 100
                short_pct = (short_liquidation / total_liquidation) * 100
            else:
                long_pct = 0
                short_pct = 0

            # 生成信号
            if total_liquidation > 500000:  # 总爆仓超过50万
                if long_liquidation > short_liquidation:
                    signal = "多单大幅爆仓，砸盘信号"
                else:
                    signal = "空单大幅爆仓，拉盘信号"
            elif len(large_liquidations) > 0:
                signal = f"检测到{len(large_liquidations)}笔大额爆仓"
            else:
                signal = "爆仓正常"

            return {
                "total_liquidation": total_liquidation,
                "long_liquidation": long_liquidation,
                "short_liquidation": short_liquidation,
                "long_pct": long_pct,
                "short_pct": short_pct,
                "large_liquidations": large_liquidations,
                "liquidation_count": len(liquidations),
                "signal": signal,
                "is_mock": False,
            }

        return self._retry_on_error(_fetch)
