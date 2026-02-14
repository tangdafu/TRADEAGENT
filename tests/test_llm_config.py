#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM API 配置测试脚本 - 演示如何使用第三方供应商 API
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings


def print_config():
    """打印当前配置"""
    print("\n" + "=" * 70)
    print("LLM API 配置信息")
    print("=" * 70)

    print("\n【当前配置】")
    print(f"  API 提供商: {settings.LLM_API_PROVIDER}")
    print(f"  模型名称: {settings.MODEL_NAME}")
    print(f"  温度: {settings.TEMPERATURE}")

    if settings.LLM_API_BASE_URL:
        print(f"  自定义 API 地址: {settings.LLM_API_BASE_URL}")
    else:
        print(f"  自定义 API 地址: (未配置，使用官方 API)")

    if settings.LLM_API_KEY:
        print(f"  自定义 API 密钥: {settings.LLM_API_KEY[:10]}...")
    else:
        print(f"  自定义 API 密钥: (未配置)")

    api_key = settings.get_llm_api_key()
    if api_key:
        print(f"  使用的 API 密钥: {api_key[:10]}...")
    else:
        print(f"  使用的 API 密钥: (未配置)")

    print("\n【配置说明】")
    print("  1. 使用官方 Anthropic API:")
    print("     - 设置 ANTHROPIC_API_KEY")
    print("     - LLM_API_PROVIDER = anthropic")
    print("     - LLM_API_BASE_URL 留空")
    print()
    print("  2. 使用第三方供应商 API:")
    print("     - 设置 LLM_API_KEY（或 ANTHROPIC_API_KEY）")
    print("     - 设置 LLM_API_BASE_URL")
    print("     - LLM_API_PROVIDER = custom")
    print()
    print("  3. 配置优先级:")
    print("     - 如果设置了 LLM_API_KEY，使用 LLM_API_KEY")
    print("     - 否则使用 ANTHROPIC_API_KEY")


def test_agent_initialization():
    """测试智能体初始化"""
    print("\n" + "=" * 70)
    print("智能体初始化测试")
    print("=" * 70)

    try:
        from src.agent.trading_agent import TradingAgent

        print("\n正在初始化交易智能体...")
        agent = TradingAgent()
        print("[OK] 智能体初始化成功！")
        print(f"  模型: {settings.MODEL_NAME}")
        print(f"  提供商: {settings.LLM_API_PROVIDER}")
        if settings.LLM_API_BASE_URL:
            print(f"  API 地址: {settings.LLM_API_BASE_URL}")

        return True

    except ValueError as e:
        print(f"[ERROR] 配置错误: {str(e)}")
        print("\n  请检查以下配置:")
        print("  - ANTHROPIC_API_KEY 或 LLM_API_KEY 是否设置")
        print("  - 密钥格式是否正确")
        return False

    except Exception as e:
        print(f"[ERROR] 初始化失败: {str(e)}")
        return False


def show_examples():
    """显示配置示例"""
    print("\n" + "=" * 70)
    print("配置示例")
    print("=" * 70)

    examples = {
        "官方 Anthropic API": """
# .env 文件
ANTHROPIC_API_KEY=sk-ant-xxxxx
LLM_API_PROVIDER=anthropic
MODEL_NAME=claude-3-5-sonnet-20241022
""",
        "AWS Bedrock": """
# .env 文件
LLM_API_PROVIDER=custom
LLM_API_BASE_URL=https://bedrock-runtime.us-east-1.amazonaws.com
LLM_API_KEY=your-aws-api-key
MODEL_NAME=anthropic.claude-3-5-sonnet-20241022-v2:0:200k
""",
        "第三方供应商": """
# .env 文件
LLM_API_PROVIDER=custom
LLM_API_BASE_URL=https://api.example.com/v1
LLM_API_KEY=your-api-key
MODEL_NAME=claude-3-5-sonnet-20241022
""",
    }

    for name, config in examples.items():
        print(f"\n【{name}】")
        print(config)


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("LLM API 配置测试工具")
    print("=" * 70)

    # 显示当前配置
    print_config()

    # 显示配置示例
    show_examples()

    # 测试智能体初始化
    success = test_agent_initialization()

    # 总结
    print("\n" + "=" * 70)
    print("总结")
    print("=" * 70)

    if success:
        print("\n[OK] 配置正确，系统已准备就绪！")
        print("\n运行分析:")
        print("  python src/main.py")
    else:
        print("\n[ERROR] 配置有问题，请检查 .env 文件")
        print("\n查看配置指南:")
        print("  cat LLM_API_CONFIG.md")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
