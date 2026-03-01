"""
准确率命令模块
包含信号表现更新功能
"""
from loguru import logger
from src.analyzers.accuracy_tracker import AccuracyTracker


def update_signal_performance(symbol: str):
    """
    更新信号表现
    
    Args:
        symbol: 交易对
    """
    try:
        tracker = AccuracyTracker()
        
        print(f"\n🔄 正在更新 {symbol} 的信号表现...")
        
        updated_count = tracker.update_signal_performance(symbol, hours=24)
        
        print(f"✅ 更新完成，共更新 {updated_count} 个信号")
        
        if updated_count > 0:
            print(f"\n💡 提示: 使用 --accuracy {symbol} 查看准确率报告")
        
    except Exception as e:
        logger.error(f"更新信号表现失败: {e}", exc_info=True)
        print(f"\n❌ 更新失败: {e}")
