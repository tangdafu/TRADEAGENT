"""
主程序入口 - 简化版
只负责命令行参数解析和路由
"""
import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置stdout为UTF-8编码以支持Unicode字符
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from loguru import logger
from src.utils.logger import setup_logger
from src.utils.setup import create_logs_directory
from src.database import init_database
from src.cli import (
    show_history,
    show_statistics,
    export_data,
    show_accuracy_report,
    update_signal_performance
)
from src.core import run_monitor_mode


def main():
    """主程序入口"""
    # 设置日志
    create_logs_directory()
    setup_logger()
    
    # 初始化数据库
    try:
        init_database()
    except Exception as e:
        logger.warning(f"数据库初始化失败: {e}")

    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="加密货币交易智能体 - 自动监控与信号追踪",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  启动监控:
    python src/main.py --symbol BTCUSDT
    python src/main.py --symbol ETHUSDT --interval 15
    python src/main.py --symbol BTCUSDT --interval 5 --verbose

  数据查询:
    python src/main.py --history BTCUSDT --days 7 --limit 10
    python src/main.py --stats BTCUSDT --days 30
    python src/main.py --export BTCUSDT

  准确率追踪:
    python src/main.py --accuracy BTCUSDT --days 30
        """
    )
    
    # 监控参数
    parser.add_argument(
        "--symbol",
        type=str,
        help="监控的交易对（必填）",
        required=False,
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=15,
        help="监控间隔（分钟），默认15分钟",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出模式",
    )
    
    # 数据查询参数
    parser.add_argument(
        "--history",
        type=str,
        metavar="SYMBOL",
        help="查询历史分析记录",
    )
    parser.add_argument(
        "--stats",
        type=str,
        metavar="SYMBOL",
        help="查看统计报告",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="查询天数，默认7天",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="查询记录数量，默认10条",
    )
    parser.add_argument(
        "--export",
        type=str,
        metavar="SYMBOL",
        help="导出数据到CSV文件",
    )
    parser.add_argument(
        "--accuracy",
        type=str,
        metavar="SYMBOL",
        help="查看信号准确率报告",
    )
    parser.add_argument(
        "--update-signals",
        type=str,
        metavar="SYMBOL",
        help="更新信号表现（追踪价格变化）",
    )

    args = parser.parse_args()

    # 判断运行模式并路由到相应的命令处理函数
    if args.history:
        # 查询历史记录
        symbol = args.history.upper()
        show_history(symbol, args.days, args.limit)
        sys.exit(0)
        
    elif args.stats:
        # 统计报告
        symbol = args.stats.upper()
        show_statistics(symbol, args.days)
        sys.exit(0)
        
    elif args.export:
        # 导出数据
        symbol = args.export.upper()
        export_data(symbol, args.days)
        sys.exit(0)
        
    elif args.accuracy:
        # 准确率报告
        symbol = args.accuracy.upper()
        show_accuracy_report(symbol, args.days)
        sys.exit(0)
        
    elif args.update_signals:
        # 更新信号表现
        symbol = args.update_signals.upper()
        update_signal_performance(symbol)
        sys.exit(0)
        
    elif args.symbol:
        # 监控模式
        symbol = args.symbol.upper()
        logger.info("=" * 70)
        logger.info("启动交易智能体分析系统")
        logger.info("=" * 70)

        try:
            run_monitor_mode([symbol], args.interval, args.verbose)
        except KeyboardInterrupt:
            logger.info("用户中断监控")
            print("\n\n程序已中断")
            sys.exit(0)

    else:
        # 没有指定参数，显示帮助
        parser.print_help()
        print("\n示例:")
        print("  启动监控: python src/main.py --symbol BTCUSDT")
        print("  查询历史: python src/main.py --history BTCUSDT --days 7")
        print("  统计报告: python src/main.py --stats BTCUSDT --days 30")
        print("  导出数据: python src/main.py --export BTCUSDT")
        print("  准确率报告: python src/main.py --accuracy BTCUSDT --days 30")
        sys.exit(1)


if __name__ == "__main__":
    main()
