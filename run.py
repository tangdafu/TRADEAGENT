#!/usr/bin/env python3
"""
快速启动脚本 - 一键运行交易分析
"""

import subprocess
import sys
from pathlib import Path

def main():
    """快速启动"""
    project_root = Path(__file__).parent

    # 检查依赖
    print("检查依赖...")
    try:
        import langchain
        import langchain_anthropic
        import binance
        import pandas
        import loguru
    except ImportError:
        print("✗ 缺少依赖，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # 检查.env文件
    env_file = project_root / ".env"
    if not env_file.exists():
        print("✗ 未找到 .env 文件")
        print("请执行以下命令进行配置:")
        print("  cp .env.example .env")
        print("  # 编辑 .env 文件，填入 ANTHROPIC_API_KEY")
        sys.exit(1)

    # 运行主程序
    print("\n启动交易智能体分析系统...\n")
    subprocess.run([sys.executable, "src/main.py"] + sys.argv[1:])

if __name__ == "__main__":
    main()
