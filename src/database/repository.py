"""
数据仓库 - 提供高级数据查询和统计功能
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger
from .models import Database, AnalysisRecord, SignalRecord, PriceRecord, SignalPerformance


class AnalysisRepository:
    """分析数据仓库"""
    
    def __init__(self, db_path: str = "data/trading_agent.db"):
        """初始化仓库"""
        self.db = Database(db_path)
    
    def save_analysis(self, symbol: str, state: Dict[str, Any], analysis_result: str) -> int:
        """
        保存完整的分析结果
        
        Args:
            symbol: 交易对
            state: LangGraph状态
            analysis_result: AI分析结果
            
        Returns:
            分析记录ID
        """
        logger.info(f"保存分析结果: {symbol}")
        
        # 提取关键信息
        kline_data = state.get('kline_volume', {})
        current_price = kline_data.get('current_price')
        price_change_24h = kline_data.get('price_change_pct')
        
        # 解析AI分析结果中的关键信息
        parsed_data = self._parse_analysis_result(analysis_result)
        
        # 构建数据
        data = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'current_price': current_price,
            'price_change_24h': price_change_24h,
            'has_trading_opportunity': state.get('has_trading_opportunity'),
            'signal_count': len(state.get('triggered_signals', [])) if state.get('has_trading_opportunity') else 0,
            'triggered_signals': ','.join(state.get('triggered_signals', [])) if state.get('has_trading_opportunity') else '',
            'trend_direction': parsed_data.get('trend_direction'),
            'confidence': parsed_data.get('confidence'),
            'support_level': parsed_data.get('support_level'),
            'resistance_level': parsed_data.get('resistance_level'),
            'stop_loss': parsed_data.get('stop_loss'),
            'target_price': parsed_data.get('target_price'),
            'suggested_position': parsed_data.get('suggested_position'),
            'full_analysis': analysis_result,
        }
        
        # 保存分析记录
        analysis_id = AnalysisRecord.create(self.db, data)
        
        # 保存价格记录
        if current_price:
            PriceRecord.create(self.db, {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'price': current_price,
                'volume_24h': kline_data.get('volume_24h'),
                'funding_rate': state.get('funding_rate', {}).get('current_rate'),
            })
        
        # 创建信号表现追踪
        if current_price and state.get('has_trading_opportunity'):
            SignalPerformance.create(
                self.db, 
                analysis_id, 
                symbol, 
                current_price, 
                datetime.now()
            )
        
        logger.info(f"分析结果已保存，ID: {analysis_id}")
        return analysis_id
    
    def _parse_analysis_result(self, analysis_text: str) -> Dict[str, Any]:
        """
        从AI分析文本中提取结构化信息
        
        Args:
            analysis_text: AI分析文本
            
        Returns:
            提取的结构化数据
        """
        result = {}
        
        try:
            lines = analysis_text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # 提取趋势方向
                if '【市场趋势判断】' in line or '市场趋势判断' in line:
                    if i + 1 < len(lines):
                        trend_line = lines[i + 1].strip()
                        if '看多' in trend_line:
                            result['trend_direction'] = '看多'
                        elif '看空' in trend_line:
                            result['trend_direction'] = '看空'
                        elif '震荡' in trend_line:
                            result['trend_direction'] = '震荡'
                
                # 提取支撑位和阻力位
                if '支撑位' in line:
                    try:
                        price = self._extract_price(line)
                        if price:
                            result['support_level'] = price
                    except:
                        pass
                
                if '阻力位' in line:
                    try:
                        price = self._extract_price(line)
                        if price:
                            result['resistance_level'] = price
                    except:
                        pass
                
                # 提取止损位
                if '止损位' in line:
                    try:
                        price = self._extract_price(line)
                        if price:
                            result['stop_loss'] = price
                    except:
                        pass
                
                # 提取目标位
                if '目标位' in line:
                    try:
                        price = self._extract_price(line)
                        if price:
                            result['target_price'] = price
                    except:
                        pass
                
                # 提取建议仓位
                if '建议仓位' in line:
                    if '轻仓' in line:
                        result['suggested_position'] = '轻仓'
                    elif '中仓' in line:
                        result['suggested_position'] = '中仓'
                    elif '重仓' in line:
                        result['suggested_position'] = '重仓'
                
                # 提取信心度
                if '信心度' in line:
                    try:
                        import re
                        match = re.search(r'(\d+)%', line)
                        if match:
                            result['confidence'] = float(match.group(1)) / 100
                    except:
                        pass
        
        except Exception as e:
            logger.warning(f"解析分析结果失败: {e}")
        
        return result
    
    def _extract_price(self, text: str) -> Optional[float]:
        """从文本中提取价格"""
        import re
        # 匹配 .56 或 1234.56 格式
        match = re.search(r'\True\s*(\d+(?:,\d{3})*(?:\.\d+)?)', text)
        if match:
            price_str = match.group(1).replace(',', '')
            return float(price_str)
        return None
    
    def get_recent_analyses(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的分析记录"""
        records = AnalysisRecord.get_recent(self.db, symbol, limit)
        return [dict(record) for record in records]
    
    def get_signal_statistics(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """
        获取信号统计信息
        
        Args:
            symbol: 交易对
            days: 统计天数
            
        Returns:
            统计数据
        """
        start_date = datetime.now() - timedelta(days=days)
        
        with self.db as conn:
            cursor = conn.cursor()
            
            # 总分析次数
            cursor.execute("""
                SELECT COUNT(*) as total_count
                FROM analysis_records
                WHERE symbol = ? AND timestamp >= ?
            """, (symbol, start_date))
            total_count = cursor.fetchone()['total_count']
            
            # 有交易机会的次数
            cursor.execute("""
                SELECT COUNT(*) as opportunity_count
                FROM analysis_records
                WHERE symbol = ? AND timestamp >= ? AND has_trading_opportunity = 1
            """, (symbol, start_date))
            opportunity_count = cursor.fetchone()['opportunity_count']
            
            # 各趋势方向统计
            cursor.execute("""
                SELECT trend_direction, COUNT(*) as count
                FROM analysis_records
                WHERE symbol = ? AND timestamp >= ? AND trend_direction IS NOT NULL
                GROUP BY trend_direction
            """, (symbol, start_date))
            trend_stats = {row['trend_direction']: row['count'] for row in cursor.fetchall()}
            
            # 平均信心度
            cursor.execute("""
                SELECT AVG(confidence) as avg_confidence
                FROM analysis_records
                WHERE symbol = ? AND timestamp >= ? AND confidence IS NOT NULL
            """, (symbol, start_date))
            avg_confidence = cursor.fetchone()['avg_confidence']
            
            return {
                'symbol': symbol,
                'period_days': days,
                'total_analyses': total_count,
                'opportunity_count': opportunity_count,
                'opportunity_rate': opportunity_count / total_count if total_count > 0 else 0,
                'trend_distribution': trend_stats,
                'avg_confidence': avg_confidence,
            }
