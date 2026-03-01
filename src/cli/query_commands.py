"""
查询命令模块
包含历史记录、统计报告、数据导出等查询功能
"""
from datetime import datetime
from pathlib import Path
from loguru import logger
from src.database import AnalysisRepository


def _log_output(message: str, level: str = "info"):
    """同时输出到控制台和日志"""
    print(message)
    # 清理emoji和特殊字符后记录到日志
    clean_msg = message.replace("✅", "").replace("⚠️", "").replace("❌", "").replace("📊", "").replace("📈", "").replace("🎯", "").strip()
    if clean_msg:
        if level == "info":
            logger.info(clean_msg)
        elif level == "warning":
            logger.warning(clean_msg)
        elif level == "error":
            logger.error(clean_msg)


def show_history(symbol: str, days: int, limit: int):
    """显示历史分析记录"""
    try:
        repo = AnalysisRepository()
        records = repo.get_recent_analyses(symbol, limit=limit)

        if not records:
            _log_output(f"\n⚠️  没有找到 {symbol} 的历史记录", "warning")
            return

        _log_output("\n" + "=" * 80)
        _log_output(f"📊 {symbol} 历史分析记录（最近 {limit} 条）")
        _log_output("=" * 80)

        for i, record in enumerate(records, 1):
            _log_output(f"\n【记录 {i}】")
            _log_output(f"时间: {record['timestamp']}")
            _log_output(f"价格: ${record['current_price']:.2f}" if record['current_price'] else "价格: N/A")
            _log_output(f"24h涨跌: {record['price_change_24h']:.2f}%" if record['price_change_24h'] else "24h涨跌: N/A")
            _log_output(f"趋势: {record['trend_direction']}" if record['trend_direction'] else "趋势: N/A")
            _log_output(f"信心度: {record['confidence']*100:.0f}%" if record['confidence'] else "信心度: N/A")
            _log_output(f"交易机会: {'是' if record['has_trading_opportunity'] else '否'}")

            if record['triggered_signals']:
                signals = record['triggered_signals'].split(',')
                _log_output(f"触发信号: {', '.join(signals)}")

            if record['suggested_position']:
                _log_output(f"建议仓位: {record['suggested_position']}")
            if record['stop_loss']:
                _log_output(f"止损位: ${record['stop_loss']:.2f}")
            if record['target_price']:
                _log_output(f"目标位: ${record['target_price']:.2f}")

            _log_output("-" * 80)

        _log_output(f"\n✅ 共查询到 {len(records)} 条记录")

    except Exception as e:
        logger.error(f"查询历史记录失败: {e}", exc_info=True)
        _log_output(f"\n❌ 查询失败: {e}", "error")


def show_statistics(symbol: str, days: int):
    """显示统计报告"""
    try:
        repo = AnalysisRepository()
        stats = repo.get_signal_statistics(symbol, days=days)

        _log_output("\n" + "=" * 80)
        _log_output(f"📈 {symbol} 统计报告（最近 {days} 天）")
        _log_output("=" * 80)

        _log_output(f"\n【基础统计】")
        _log_output(f"总分析次数: {stats['total_analyses']}")
        _log_output(f"交易机会次数: {stats['opportunity_count']}")
        _log_output(f"机会率: {stats['opportunity_rate']*100:.1f}%")

        if stats.get('avg_confidence'):
            _log_output(f"平均信心度: {stats['avg_confidence']*100:.1f}%")

        if stats.get('trend_distribution'):
            _log_output(f"\n【趋势分布】")
            for trend, count in stats['trend_distribution'].items():
                _log_output(f"{trend}: {count} 次")

        if stats.get('top_signals'):
            _log_output(f"\n【高频信号】")
            for signal, count in stats['top_signals']:
                _log_output(f"{signal}: {count} 次")

        if stats.get('avg_price'):
            _log_output(f"\n【价格统计】")
            _log_output(f"平均价格: ${stats['avg_price']:.2f}")
            if stats.get('price_range'):
                _log_output(f"价格区间: ${stats['price_range'][0]:.2f} - ${stats['price_range'][1]:.2f}")

        _log_output("\n【分析频率】")
        _log_output(f"平均每天分析: {stats['total_analyses'] / max(days, 1):.1f} 次")

        _log_output("\n" + "=" * 80)

    except Exception as e:
        logger.error(f"生成统计报告失败: {e}", exc_info=True)
        _log_output(f"\n❌ 统计失败: {e}", "error")


def export_data(symbol: str, days: int):
    """导出数据到CSV文件"""
    try:
        repo = AnalysisRepository()
        records = repo.get_recent_analyses(symbol, limit=10000)

        if not records:
            _log_output(f"\n⚠️  没有找到 {symbol} 的数据", "warning")
            return

        # 创建导出目录
        export_dir = Path("data")
        export_dir.mkdir(exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = export_dir / f"export_{symbol}_{timestamp}.csv"

        # 写入CSV
        import csv
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # 写入表头
            writer.writerow([
                '时间', '价格', '24h涨跌%', '趋势', '信心度%',
                '交易机会', '触发信号', '建议仓位', '止损位', '目标位'
            ])

            # 写入数据
            for record in records:
                writer.writerow([
                    record['timestamp'],
                    record['current_price'] or '',
                    record['price_change_24h'] or '',
                    record['trend_direction'] or '',
                    f"{record['confidence']*100:.0f}" if record['confidence'] else '',
                    '是' if record['has_trading_opportunity'] else '否',
                    record['triggered_signals'] or '',
                    record['suggested_position'] or '',
                    record['stop_loss'] or '',
                    record['target_price'] or ''
                ])

        _log_output(f"\n✅ 数据已导出到: {filename}")
        _log_output(f"📊 共导出 {len(records)} 条记录")

    except Exception as e:
        logger.error(f"导出数据失败: {e}", exc_info=True)
        _log_output(f"\n❌ 导出失败: {e}", "error")


def show_accuracy_report(symbol: str, days: int):
    """显示信号准确率报告"""
    try:
        from src.analyzers.accuracy_tracker import AccuracyTracker

        tracker = AccuracyTracker()
        report = tracker.get_accuracy_report(symbol, days=days)

        if not report:
            _log_output(f"\n⚠️  没有找到 {symbol} 的信号数据", "warning")
            _log_output("提示: 请先运行 --update-signals 更新信号表现")
            return

        _log_output("\n" + "=" * 80)
        _log_output(f"🎯 {symbol} 信号准确率报告（最近 {days} 天）")
        _log_output("=" * 80)

        _log_output(f"\n【总体统计】")
        _log_output(f"总信号数: {report['total_signals']}")
        _log_output(f"已关闭信号: {report['closed_signals']}")
        _log_output(f"盈利信号: {report['profitable_signals']}")
        _log_output(f"亏损信号: {report['loss_signals']}")
        _log_output(f"准确率: {report['accuracy']*100:.1f}%")

        if report.get('avg_profit'):
            _log_output(f"\n【收益统计】")
            _log_output(f"平均收益: {report['avg_profit']:.2f}%")
            _log_output(f"最大收益: {report['max_profit']:.2f}%")
            _log_output(f"最大亏损: {report['max_loss']:.2f}%")

        if report.get('signal_performance'):
            _log_output(f"\n【信号表现】")
            for signal_type, perf in report['signal_performance'].items():
                _log_output(f"\n{signal_type}:")
                _log_output(f"  触发次数: {perf['count']}")
                _log_output(f"  准确率: {perf['accuracy']*100:.1f}%")
                _log_output(f"  平均收益: {perf['avg_profit']:.2f}%")

        _log_output("\n" + "=" * 80)

    except Exception as e:
        logger.error(f"生成准确率报告失败: {e}", exc_info=True)
        _log_output(f"\n❌ 报告生成失败: {e}", "error")
