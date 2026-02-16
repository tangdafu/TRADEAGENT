"""
主程序入口 - LangGraph 版本
使用 LangGraph 实现并行数据采集和状态管理
"""
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
from src.workflow.trading_graph import run_trading_analysis


def create_logs_directory():
    """创建日志目录"""
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)


def main():
    """主程序入口 - LangGraph版本"""
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
        description="BTC/ETH合约交易智能体 - 基于LangGraph的并行数据采集系统"
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

    logger.info("=" * 70)
    logger.info("启动交易智能体分析系统 (LangGraph版本)")
    logger.info(f"交易对: {symbol}")
    logger.info(f"详细模式: {'开启' if args.verbose else '关闭'}")
    logger.info("=" * 70)

    try:
        print(f"\n【数据采集中】正在并行采集 {symbol} 的市场数据...\n")

        # 运行 LangGraph 工作流
        final_state = run_trading_analysis(symbol, args.verbose)

        # 检查是否有分析结果
        if not final_state["analysis_result"]:
            error_msg = "AI分析失败，无法生成分析报告"
            if final_state["errors"]:
                error_msg += f"\n错误详情:\n" + "\n".join(f"  - {e}" for e in final_state["errors"])
            print(format_error_message(error_msg))
            sys.exit(1)

        # 输出结果
        if args.verbose and final_state["formatted_data"]:
            print("\n" + "=" * 70)
            print("【原始数据】")
            print("=" * 70)
            print(final_state["formatted_data"])
            print("\n" + "=" * 70 + "\n")

        # 格式化并显示分析报告
        output = format_analysis_output(symbol, final_state["analysis_result"])
        print(output)

        # 显示工作流统计信息
        if args.verbose:
            print("\n" + "=" * 70)
            print("【工作流统计】")
            print("=" * 70)
            print(f"数据采集节点: 4个 (并行执行)")
            print(f"  - 资金费率: {'✓' if final_state['funding_rate'] else '✗'}")
            print(f"  - K线数据: {'✓' if final_state['kline_volume'] else '✗'}")
            print(f"  - 爆仓数据: {'✓' if final_state['liquidation'] else '✗'}")
            print(f"  - 消息面数据: {'✓' if final_state['news_sentiment'] else '✗'}")
            print(f"错误数量: {len(final_state['errors'])}")
            print("=" * 70)

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
