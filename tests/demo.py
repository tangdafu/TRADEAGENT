#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示脚本 - 展示系统如何工作
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data_collectors.funding_rate import FundingRateCollector
from src.data_collectors.kline_volume import KlineVolumeCollector
from src.data_collectors.liquidation import LiquidationCollector
from src.analyzers.factor_analyzer import FactorAnalyzer


def demo():
    """演示系统功能"""
    print("\n" + "=" * 70)
    print("交易智能体系统 - 功能演示")
    print("=" * 70)

    symbol = "BTCUSDT"
    print(f"\n正在采集 {symbol} 的市场数据...\n")

    try:
        # 创建分析器
        analyzer = FactorAnalyzer()

        # 采集数据
        print("[1] 采集资金费率数据...")
        funding_data = analyzer.funding_rate_collector.collect(symbol)
        print(f"    当前资金费率: {funding_data['current_rate']:.6f}")
        print(f"    24小时平均: {funding_data['avg_rate_24h']:.6f}")
        print(f"    趋势: {funding_data['trend']}")
        print(f"    信号: {funding_data['signal']}")

        print("\n[2] 采集K线和成交量数据...")
        kline_data = analyzer.kline_volume_collector.collect(symbol)
        print(f"    当前价格: ${kline_data['current_price']:.2f}")
        print(f"    24小时最高: ${kline_data['highest_price_24h']:.2f}")
        print(f"    24小时最低: ${kline_data['lowest_price_24h']:.2f}")
        print(f"    价格变化: {kline_data['price_change_pct']:.2f}%")
        print(f"    价格趋势: {kline_data['price_trend']}")
        print(f"    支撑位: ${kline_data['support']:.2f}")
        print(f"    阻力位: ${kline_data['resistance']:.2f}")
        print(f"    成交量信号: {kline_data['volume_signal']}")

        print("\n[3] 采集爆仓数据...")
        liquidation_data = analyzer.liquidation_collector.collect(symbol)
        print(f"    总爆仓金额: ${liquidation_data['total_liquidation']:,.0f}")
        print(f"    多单爆仓: ${liquidation_data['long_liquidation']:,.0f} ({liquidation_data['long_pct']:.1f}%)")
        print(f"    空单爆仓: ${liquidation_data['short_liquidation']:,.0f} ({liquidation_data['short_pct']:.1f}%)")
        print(f"    爆仓笔数: {liquidation_data['liquidation_count']}")
        print(f"    信号: {liquidation_data['signal']}")

        # 格式化数据
        print("\n[4] 格式化数据用于AI分析...")
        analysis_data = {
            "symbol": symbol,
            "funding_rate": funding_data,
            "kline_volume": kline_data,
            "liquidation": liquidation_data,
        }
        formatted_data = analyzer.format_for_llm(analysis_data)
        print("\n【格式化后的数据】")
        print(formatted_data)

        print("\n" + "=" * 70)
        print("数据采集完成！")
        print("=" * 70)

        print("\n下一步:")
        print("1. 在 .env 文件中填入 ANTHROPIC_API_KEY")
        print("2. 运行: python src/main.py")
        print("3. 系统将使用Claude进行深度分析并给出交易建议")

        return 0

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(demo())
