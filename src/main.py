import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置stdout为UTF-8编码以支持Unicode字符
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from loguru import logger
from config.settings import settings
from src.utils.logger import setup_logger
from src.utils.formatters import format_analysis_output, format_error_message
from src.analyzers.factor_analyzer import FactorAnalyzer
from src.agent.trading_agent import TradingAgent


def create_logs_directory():
    """创建日志目录"""
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)


def main():
    """主程序入口"""
    # 设置日志
    create_logs_directory()
    setup_logger()

    # 验证配置
    try:
        settings.validate()
    except ValueError as e:
        print(format_error_message(str(e)))
        sys.exit(1)

    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="BTC/ETH合约交易智能体 - 基于LangChain和Claude的AI交易分析系统"
    )
    parser.add_argument(
        "--symbol",
        type=str,
        default="ETHUSDT",
        help="交易对 (默认: ETHUSDT)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出模式",
    )

    args = parser.parse_args()
    symbol = args.symbol.upper()

    logger.info(f"启动交易智能体分析系统")
    logger.info(f"交易对: {symbol}")

    try:
        # 1. 初始化分析器
        logger.info("初始化数据分析器...")
        analyzer = FactorAnalyzer()

        # 2. 采集数据
        logger.info("采集市场数据...")
        print(f"\n【数据采集中】正在采集 {symbol} 的市场数据...\n")

        analysis_data = analyzer.analyze_all_factors(symbol)

        # 3. 格式化数据
        logger.info("格式化数据...")
        formatted_data = analyzer.format_for_llm(analysis_data)

        if args.verbose:
            print("【原始数据】")
            print(formatted_data)
            print("\n" + "=" * 70 + "\n")

        # 4. 初始化交易智能体
        logger.info("初始化交易智能体...")
        agent = TradingAgent()

        # 5. 调用AI分析
        logger.info("调用Claude进行分析...")
        print("【AI分析中】正在调用Claude进行深度分析...\n")

        analysis_result = agent.analyze(formatted_data)

        # 6. 输出结果
        output = format_analysis_output(symbol, analysis_result)
        print(output)

        logger.info("分析完成")

    except KeyboardInterrupt:
        logger.info("用户中断程序")
        print("\n\n程序已中断")
        sys.exit(0)

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}", exc_info=True)
        print(format_error_message(f"程序执行出错: {str(e)}"))
        sys.exit(1)


if __name__ == "__main__":
    main()
