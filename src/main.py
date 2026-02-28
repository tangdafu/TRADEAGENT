"""
主程序入口 - LangGraph 版本
使用 LangGraph 实现并行数据采集和状态管理
支持单次分析和定时监控两种模式
"""
import argparse
import sys
import os
import time
import signal
from pathlib import Path
from datetime import datetime

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
from src.database import init_database, AnalysisRepository
from src.scheduler import AlertManager

# 全局变量用于优雅退出
running = True


def signal_handler(signum, frame):
    """处理中断信号"""
    global running
    running = False
    logger.info("收到退出信号，正在停止...")


def create_logs_directory():
    """创建日志目录"""
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)


def run_single_analysis(symbol: str, verbose: bool, save: bool) -> bool:
    """
    运行单次分析
    
    Args:
        symbol: 交易对
        verbose: 是否显示详细信息
        save: 是否保存到数据库
        
    Returns:
        bool: 分析是否成功
    """
    try:
        print(f"\n【数据采集中】正在并行采集 {symbol} 的市场数据...\n")

        # 运行 LangGraph 工作流
        final_state = run_trading_analysis(symbol, verbose)

        # 检查是否有分析结果
        if not final_state.get("analysis_result"):
            error_msg = "AI分析失败，无法生成分析报告"
            if final_state.get("errors"):
                error_msg += f"\n错误详情:\n" + "\n".join(f"  - {e}" for e in final_state["errors"])
            print(format_error_message(error_msg))
            return False

        # 输出结果
        if verbose and final_state.get("formatted_data"):
            print("\n" + "=" * 70)
            print("【原始数据】")
            print("=" * 70)
            print(final_state["formatted_data"])
            print("\n" + "=" * 70 + "\n")

        # 格式化并显示分析报告
        output = format_analysis_output(symbol, final_state["analysis_result"])
        print(output)
        
        # 保存到数据库
        if save:
            try:
                repo = AnalysisRepository()
                analysis_id = repo.save_analysis(symbol, final_state, final_state["analysis_result"])
                logger.info(f"分析结果已保存到数据库，记录ID: {analysis_id}")
                print(f"\n[数据库] 分析结果已保存 (ID: {analysis_id})")
            except Exception as e:
                logger.error(f"保存到数据库失败: {e}")
                print(f"\n[警告] 保存到数据库失败: {e}")

        # 显示工作流统计信息
        if verbose:
            print("\n" + "=" * 70)
            print("【工作流统计】")
            print("=" * 70)
            print(f"数据采集节点: 4个 (并行执行)")
            print(f"  - 资金费率: {'✓' if final_state.get('funding_rate') else '✗'}")
            print(f"  - K线数据: {'✓' if final_state.get('kline_volume') else '✗'}")
            print(f"  - 市场压力数据: {'✓' if final_state.get('liquidation') else '✗'}")
            print(f"  - 消息面数据: {'✓' if final_state.get('news_sentiment') else '✗'}")
            print(f"错误数量: {len(final_state.get('errors', []))}")
            print("=" * 70)

        logger.info("分析完成")
        return True

    except KeyboardInterrupt:
        logger.info("用户中断分析")
        print("\n\n程序已中断")
        return False
    except Exception as e:
        logger.error(f"分析过程出错: {e}", exc_info=True)
        print(format_error_message(f"分析失败: {e}"))
        return False


def run_monitor_mode(symbols: list, interval: int, verbose: bool):
    """
    运行监控模式
    
    Args:
        symbols: 监控的交易对列表
        interval: 监控间隔（分钟）
        verbose: 是否显示详细信息
    """
    global running
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 初始化告警管理器
    alert_manager = AlertManager()
    
    logger.info("=" * 70)
    logger.info("启动监控模式")
    logger.info(f"监控币种: {', '.join(symbols)}")
    logger.info(f"监控间隔: {interval} 分钟")
    logger.info("自动保存: 开启")
    logger.info("=" * 70)
    
    print("\n" + "=" * 70)
    print("🔄 监控模式已启动")
    print(f"📊 监控币种: {', '.join(symbols)}")
    print(f"⏰ 监控间隔: {interval} 分钟")
    print("💾 自动保存: 开启")
    print(f"📱 飞书告警: {'开启' if alert_manager.feishu_enabled else '关闭'}")
    print("\n按 Ctrl+C 停止监控")
    print("=" * 70 + "\n")
    
    analysis_count = 0
    
    while running:
        try:
            analysis_count += 1
            
            for symbol in symbols:
                if not running:
                    break
                
                logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始分析 {symbol} (第 {analysis_count} 次)")
                
                print("\n" + "=" * 70)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 分析 {symbol} (第 {analysis_count} 次)")
                print("=" * 70)
                
                # 运行分析
                final_state = run_trading_analysis(symbol, verbose)
                
                if final_state.get("analysis_result"):
                    # 保存到数据库
                    try:
                        repo = AnalysisRepository()
                        analysis_result = final_state["analysis_result"]
                        analysis_id = repo.save_analysis(symbol, final_state, analysis_result)
                        logger.info(f"分析结果已保存，ID: {analysis_id}")
                        
                        # 检查是否有交易机会
                        has_opportunity = final_state.get("has_trading_opportunity", False)
                        
                        if has_opportunity:
                            # 从final_state中提取数据用于告警
                            kline_data = final_state.get('kline_volume', {})
                            alert_data = {
                                'current_price': kline_data.get('current_price'),
                                'price_change_24h': kline_data.get('price_change_pct'),
                                'trend_direction': '未知',
                                'confidence': 0,
                                'triggered_signals': final_state.get('triggered_signals', []),
                                'suggested_position': None,
                                'stop_loss': None,
                                'target_price': None
                            }
                            
                            # 简单解析趋势方向
                            if isinstance(analysis_result, str):
                                if '上涨' in analysis_result or '做多' in analysis_result:
                                    alert_data['trend_direction'] = '上涨'
                                elif '下跌' in analysis_result or '做空' in analysis_result:
                                    alert_data['trend_direction'] = '下跌'
                                else:
                                    alert_data['trend_direction'] = '震荡'
                            
                            # 传递完整的AI分析文本
                            alert_manager.send_alert(symbol, alert_data, analysis_result)
                            print(f"\n✅ 检测到交易机会！已发送告警（含完整AI策略）")
                        else:
                            print(f"\n⏸️  暂无交易机会")
                            
                    except Exception as e:
                        logger.error(f"保存分析结果失败: {e}", exc_info=True)
                        print(f"\n⚠️  保存失败: {e}")
                else:
                    logger.warning(f"{symbol} 分析失败")
                    print(f"\n⚠️  {symbol} 分析失败")
            
            if not running:
                break
                
            # 等待下一次执行
            wait_seconds = interval * 60
            print(f"\n⏰ 下次分析时间: {interval} 分钟后")
            
            # 分段等待，以便能够响应中断信号
            for _ in range(wait_seconds):
                if not running:
                    break
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"监控循环出错: {e}", exc_info=True)
            print(f"\n❌ 监控出错: {e}")
            time.sleep(60)  # 出错后等待1分钟再继续
    
    logger.info("监控已停止")
    print(f"\n\n✅ 监控已停止，共完成 {analysis_count} 次分析")


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

    # 验证配置
    try:
        settings.validate()
    except ValueError as e:
        print(format_error_message(str(e)))
        sys.exit(1)

    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="加密货币交易智能体 - 支持单次分析和定时监控",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  单次分析:
    python src/main.py --symbol BTCUSDT
    python src/main.py --symbol BTCUSDT --save
    
  监控模式:
    python src/main.py --symbols BTCUSDT ETHUSDT --interval 15
    python src/main.py --symbols BTCUSDT --interval 5 --verbose
        """
    )
    
    parser.add_argument(
        "--symbol",
        type=str,
        help="交易对 (单次分析模式)",
    )
    parser.add_argument(
        "--symbols",
        type=str,
        nargs="+",
        help="监控的交易对列表 (监控模式)",
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
    parser.add_argument(
        "--save",
        action="store_true",
        help="保存分析结果到数据库（单次分析模式，监控模式默认保存）",
    )

    args = parser.parse_args()

    # 判断运行模式
    if args.symbols:
        # 监控模式
        symbols = [s.upper() for s in args.symbols]
        logger.info("=" * 70)
        logger.info("启动交易智能体分析系统 - 监控模式")
        logger.info("=" * 70)
        
        try:
            run_monitor_mode(symbols, args.interval, args.verbose)
        except KeyboardInterrupt:
            logger.info("用户中断监控")
            print("\n\n程序已中断")
            sys.exit(0)
            
    elif args.symbol:
        # 单次分析模式
        symbol = args.symbol.upper()
        logger.info("=" * 70)
        logger.info("启动交易智能体分析系统 - 单次分析模式")
        logger.info(f"交易对: {symbol}")
        logger.info(f"详细模式: {'开启' if args.verbose else '关闭'}")
        logger.info(f"数据库保存: {'开启' if args.save else '关闭'}")
        logger.info("=" * 70)
        
        try:
            success = run_single_analysis(symbol, args.verbose, args.save)
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            logger.info("用户中断程序")
            print("\n\n程序已中断")
            sys.exit(0)
            
    else:
        # 没有指定参数，显示帮助
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
