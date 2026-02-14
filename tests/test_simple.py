#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的测试脚本 - 验证系统各个模块是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """测试所有模块导入"""
    print("\n[1] 测试模块导入...")

    try:
        from config.settings import settings
        print("  OK - 配置模块导入成功")

        from src.data_collectors.base import BaseCollector
        from src.data_collectors.funding_rate import FundingRateCollector
        from src.data_collectors.kline_volume import KlineVolumeCollector
        from src.data_collectors.liquidation import LiquidationCollector
        print("  OK - 数据采集模块导入成功")

        from src.analyzers.factor_analyzer import FactorAnalyzer
        print("  OK - 数据分析模块导入成功")

        from src.agent.trading_agent import TradingAgent
        from src.agent.prompts import get_analysis_prompt
        print("  OK - 智能体模块导入成功")

        from src.utils.logger import setup_logger
        from src.utils.formatters import format_analysis_output, format_error_message
        print("  OK - 工具模块导入成功")

        return True

    except Exception as e:
        print(f"  ERROR - 模块导入失败: {str(e)}")
        return False


def test_config():
    """测试配置"""
    print("\n[2] 测试配置...")

    try:
        from config.settings import settings

        print(f"  - 模型: {settings.MODEL_NAME}")
        print(f"  - 日志级别: {settings.LOG_LEVEL}")
        print(f"  - 交易对: {settings.SYMBOL}")

        print("  OK - 配置验证成功")
        return True

    except Exception as e:
        print(f"  ERROR - 配置验证失败: {str(e)}")
        return False


def test_collectors():
    """测试数据采集器初始化"""
    print("\n[3] 测试数据采集器初始化...")

    try:
        from src.data_collectors.funding_rate import FundingRateCollector
        from src.data_collectors.kline_volume import KlineVolumeCollector
        from src.data_collectors.liquidation import LiquidationCollector

        fr_collector = FundingRateCollector()
        print("  OK - 资金费率采集器初始化成功")

        kv_collector = KlineVolumeCollector()
        print("  OK - K线成交量采集器初始化成功")

        lq_collector = LiquidationCollector()
        print("  OK - 爆仓数据采集器初始化成功")

        return True

    except Exception as e:
        print(f"  ERROR - 采集器初始化失败: {str(e)}")
        return False


def test_analyzer():
    """测试分析器初始化"""
    print("\n[4] 测试分析器初始化...")

    try:
        from src.analyzers.factor_analyzer import FactorAnalyzer

        analyzer = FactorAnalyzer()
        print("  OK - 因素分析器初始化成功")

        return True

    except Exception as e:
        print(f"  ERROR - 分析器初始化失败: {str(e)}")
        return False


def test_agent():
    """测试交易智能体初始化"""
    print("\n[5] 测试交易智能体初始化...")

    try:
        from src.agent.trading_agent import TradingAgent

        agent = TradingAgent()
        print("  OK - 交易智能体初始化成功")

        return True

    except ValueError as e:
        print(f"  WARNING - 智能体初始化需要API密钥: {str(e)}")
        print("  提示: 请在 .env 文件中设置 ANTHROPIC_API_KEY")
        return True  # 这不是失败，只是需要配置

    except Exception as e:
        print(f"  ERROR - 智能体初始化失败: {str(e)}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("交易智能体系统 - 模块测试")
    print("=" * 70)

    tests = [
        ("模块导入", test_imports),
        ("配置验证", test_config),
        ("采集器初始化", test_collectors),
        ("分析器初始化", test_analyzer),
        ("智能体初始化", test_agent),
    ]

    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))

    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "OK" if result else "FAIL"
        print(f"  [{status}] {test_name}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n[SUCCESS] 所有测试通过！系统已准备就绪。")
        print("\n使用方法:")
        print("  python src/main.py                    # 分析BTC")
        print("  python src/main.py --symbol ETHUSDT   # 分析ETH")
        print("  python src/main.py --verbose          # 详细输出")
        return 0
    else:
        print("\n[FAILED] 部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
