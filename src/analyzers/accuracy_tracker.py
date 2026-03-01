"""
信号准确率追踪模块
追踪信号触发后的价格变化，计算准确率
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
from loguru import logger
from src.database import AnalysisRepository
from src.data_collectors.kline_volume import KlineVolumeCollector


class AccuracyTracker:
    """信号准确率追踪器"""
    
    def __init__(self):
        """初始化追踪器"""
        self.repo = AnalysisRepository()
        self.kline_collector = KlineVolumeCollector()
    
    def update_signal_performance(self, symbol: str, hours: int = 24) -> int:
        """
        更新信号表现

        Args:
            symbol: 交易对
            hours: 追踪小时数

        Returns:
            int: 更新的信号数量
        """
        updated_count = 0  # 添加计数器

        try:
            # 获取需要更新的信号记录
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with self.repo.db as conn:
                cursor = conn.cursor()
                
                # 查询未更新的信号记录
                cursor.execute("""
                    SELECT sp.id, sp.analysis_id, sp.symbol, sp.entry_price, sp.entry_time,
                           ar.trend_direction, ar.target_price, ar.stop_loss
                    FROM signal_performance sp
                    JOIN analysis_records ar ON sp.analysis_id = ar.id
                    WHERE sp.symbol = ? 
                    AND sp.entry_time >= ?
                    AND sp.exit_price IS NULL
                    ORDER BY sp.entry_time DESC
                """, (symbol, cutoff_time))
                
                pending_signals = cursor.fetchall()

                if not pending_signals:
                    logger.info(f"没有需要更新的信号记录: {symbol}")
                    return updated_count
                
                logger.info(f"找到 {len(pending_signals)} 条待更新的信号记录")
                
                # 获取当前价格
                current_data = self.kline_collector.collect(symbol)
                current_price = current_data.get('current_price')

                if not current_price:
                    logger.warning("无法获取当前价格")
                    return updated_count
                
                # 更新每条记录
                for signal in pending_signals:
                    signal_id = signal['id']
                    entry_price = signal['entry_price']
                    entry_time = datetime.fromisoformat(signal['entry_time'])
                    trend = signal['trend_direction']
                    target_price = signal['target_price']
                    stop_loss = signal['stop_loss']
                    
                    # 计算价格变化
                    price_change_pct = ((current_price - entry_price) / entry_price) * 100
                    
                    # 判断是否达到目标或止损
                    hit_target = False
                    hit_stop_loss = False
                    is_profitable = False
                    
                    if trend == '上涨' or trend == '看多':
                        # 做多信号
                        if target_price and current_price >= target_price:
                            hit_target = True
                            is_profitable = True
                        elif stop_loss and current_price <= stop_loss:
                            hit_stop_loss = True
                            is_profitable = False
                        else:
                            is_profitable = price_change_pct > 0
                    
                    elif trend == '下跌' or trend == '看空':
                        # 做空信号
                        if target_price and current_price <= target_price:
                            hit_target = True
                            is_profitable = True
                        elif stop_loss and current_price >= stop_loss:
                            hit_stop_loss = True
                            is_profitable = False
                        else:
                            is_profitable = price_change_pct < 0
                    
                    # 检查是否应该关闭信号（达到目标、止损或超过24小时）
                    hours_elapsed = (datetime.now() - entry_time).total_seconds() / 3600
                    should_close = hit_target or hit_stop_loss or hours_elapsed >= 24
                    
                    if should_close:
                        # 更新记录
                        cursor.execute("""
                            UPDATE signal_performance
                            SET exit_price = ?,
                                exit_time = ?,
                                price_change_pct = ?,
                                hit_target = ?,
                                hit_stop_loss = ?,
                                is_profitable = ?
                            WHERE id = ?
                        """, (
                            current_price,
                            datetime.now(),
                            price_change_pct,
                            1 if hit_target else 0,
                            1 if hit_stop_loss else 0,
                            1 if is_profitable else 0,
                            signal_id
                        ))

                        updated_count += 1  # 增加计数

                        logger.info(f"信号 {signal_id} 已关闭: "
                                  f"{'盈利' if is_profitable else '亏损'}, "
                                  f"价格变化: {price_change_pct:.2f}%")

                conn.commit()
                logger.info(f"信号表现更新完成: {symbol}, 更新了 {updated_count} 条记录")
                return updated_count  # 返回更新计数

        except Exception as e:
            logger.error(f"更新信号表现失败: {e}", exc_info=True)
            return updated_count  # 异常时也返回计数
    
    def get_accuracy_report(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        获取准确率报告
        
        Args:
            symbol: 交易对
            days: 统计天数
            
        Returns:
            准确率报告
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            with self.repo.db as conn:
                cursor = conn.cursor()
                
                # 总信号数
                cursor.execute("""
                    SELECT COUNT(*) as total
                    FROM signal_performance
                    WHERE symbol = ? AND entry_time >= ?
                """, (symbol, cutoff_time))
                total_signals = cursor.fetchone()['total']
                
                # 已关闭的信号数
                cursor.execute("""
                    SELECT COUNT(*) as closed
                    FROM signal_performance
                    WHERE symbol = ? AND entry_time >= ? AND exit_price IS NOT NULL
                """, (symbol, cutoff_time))
                closed_signals = cursor.fetchone()['closed']
                
                # 盈利信号数
                cursor.execute("""
                    SELECT COUNT(*) as profitable
                    FROM signal_performance
                    WHERE symbol = ? AND entry_time >= ? 
                    AND exit_price IS NOT NULL AND is_profitable = 1
                """, (symbol, cutoff_time))
                profitable_signals = cursor.fetchone()['profitable']
                
                # 达到目标的信号数
                cursor.execute("""
                    SELECT COUNT(*) as hit_target
                    FROM signal_performance
                    WHERE symbol = ? AND entry_time >= ? 
                    AND exit_price IS NOT NULL AND hit_target = 1
                """, (symbol, cutoff_time))
                hit_target_signals = cursor.fetchone()['hit_target']
                
                # 触发止损的信号数
                cursor.execute("""
                    SELECT COUNT(*) as hit_stop
                    FROM signal_performance
                    WHERE symbol = ? AND entry_time >= ? 
                    AND exit_price IS NOT NULL AND hit_stop_loss = 1
                """, (symbol, cutoff_time))
                hit_stop_signals = cursor.fetchone()['hit_stop']
                
                # 平均价格变化
                cursor.execute("""
                    SELECT AVG(price_change_pct) as avg_change
                    FROM signal_performance
                    WHERE symbol = ? AND entry_time >= ? 
                    AND exit_price IS NOT NULL
                """, (symbol, cutoff_time))
                avg_change = cursor.fetchone()['avg_change'] or 0
                
                # 按趋势分类统计
                cursor.execute("""
                    SELECT ar.trend_direction, 
                           COUNT(*) as total,
                           SUM(CASE WHEN sp.is_profitable = 1 THEN 1 ELSE 0 END) as profitable
                    FROM signal_performance sp
                    JOIN analysis_records ar ON sp.analysis_id = ar.id
                    WHERE sp.symbol = ? AND sp.entry_time >= ? 
                    AND sp.exit_price IS NOT NULL
                    GROUP BY ar.trend_direction
                """, (symbol, cutoff_time))
                trend_stats = cursor.fetchall()
                
                # 计算准确率
                accuracy = (profitable_signals / closed_signals * 100) if closed_signals > 0 else 0
                target_hit_rate = (hit_target_signals / closed_signals * 100) if closed_signals > 0 else 0
                
                return {
                    'symbol': symbol,
                    'period_days': days,
                    'total_signals': total_signals,
                    'closed_signals': closed_signals,
                    'pending_signals': total_signals - closed_signals,
                    'profitable_signals': profitable_signals,
                    'accuracy': accuracy,
                    'hit_target_signals': hit_target_signals,
                    'target_hit_rate': target_hit_rate,
                    'hit_stop_signals': hit_stop_signals,
                    'avg_price_change': avg_change,
                    'trend_stats': [dict(row) for row in trend_stats]
                }
                
        except Exception as e:
            logger.error(f"生成准确率报告失败: {e}", exc_info=True)
            return {}
