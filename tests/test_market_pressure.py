"""
测试市场压力数据采集器（替代爆仓数据）
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_collectors.liquidation import LiquidationCollector


def test_market_pressure_collector():
    """测试市场压力数据采集"""
    print("=" * 70)
    print("测试市场压力数据采集器")
    print("=" * 70)

    collector = LiquidationCollector()

    # 测试 BTC
    print("\n【测试 BTCUSDT】")
    btc_data = collector.collect("BTCUSDT")

    print(f"数据可用: {btc_data['data_available']}")
    print(f"持仓量: {btc_data['open_interest']}")
    print(f"多空比: {btc_data['long_short_ratio']}")
    print(f"多头占比: {btc_data['long_account_pct']:.2f}%")
    print(f"空头占比: {btc_data['short_account_pct']:.2f}%")
    print(f"买卖比: {btc_data['buy_sell_ratio']}")
    print(f"主动买量: {btc_data['buy_volume']}")
    print(f"主动卖量: {btc_data['sell_volume']}")
    print(f"风险等级: {btc_data['risk_level']}")
    print(f"信号: {btc_data['signal']}")

    # 测试 ETH
    print("\n【测试 ETHUSDT】")
    eth_data = collector.collect("ETHUSDT")

    print(f"数据可用: {eth_data['data_available']}")
    print(f"持仓量: {eth_data['open_interest']}")
    print(f"多空比: {eth_data['long_short_ratio']}")
    print(f"多头占比: {eth_data['long_account_pct']:.2f}%")
    print(f"空头占比: {eth_data['short_account_pct']:.2f}%")
    print(f"买卖比: {eth_data['buy_sell_ratio']}")
    print(f"风险等级: {eth_data['risk_level']}")
    print(f"信号: {eth_data['signal']}")

    print("\n" + "=" * 70)
    print("测试完成！市场压力数据采集正常")
    print("=" * 70)


if __name__ == "__main__":
    test_market_pressure_collector()
