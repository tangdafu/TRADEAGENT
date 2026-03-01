"""
数据库模型定义
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger


class Database:
    def __init__(self, db_path: str = "data/trading_agent.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        
    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.close()


def init_database(db_path: str = "data/trading_agent.db"):
    logger.info(f"初始化数据库: {db_path}")
    db = Database(db_path)
    with db as conn:
        cursor = conn.cursor()
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS analysis_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            current_price REAL,
            price_change_24h REAL,
            has_trading_opportunity BOOLEAN,
            signal_count INTEGER,
            triggered_signals TEXT,
            trend_direction TEXT,
            confidence REAL,
            support_level REAL,
            resistance_level REAL,
            stop_loss REAL,
            target_price REAL,
            suggested_position TEXT,
            full_analysis TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            
        cursor.execute("""CREATE TABLE IF NOT EXISTS signal_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            symbol TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            signal_type TEXT NOT NULL,
            signal_strength TEXT,
            signal_value REAL,
            signal_description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            
        cursor.execute("""CREATE TABLE IF NOT EXISTS price_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            price REAL NOT NULL,
            volume_24h REAL,
            funding_rate REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            
        cursor.execute("""CREATE TABLE IF NOT EXISTS signal_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            symbol TEXT NOT NULL,
            entry_price REAL NOT NULL,
            entry_time DATETIME NOT NULL,
            price_1h REAL,
            price_4h REAL,
            price_24h REAL,
            return_1h REAL,
            return_4h REAL,
            return_24h REAL,
            hit_target BOOLEAN,
            hit_stop_loss BOOLEAN,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS processed_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            news_id TEXT NOT NULL,
            title TEXT NOT NULL,
            source TEXT,
            published_time INTEGER NOT NULL,
            sentiment TEXT,
            processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, news_id))""")

        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_analysis_symbol_time
            ON analysis_records(symbol, timestamp DESC)""")

        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_processed_news_symbol_time
            ON processed_news(symbol, published_time DESC)""")
            
        conn.commit()
        logger.info("数据库初始化完成")


class AnalysisRecord:
    @staticmethod
    def create(db: Database, data: Dict[str, Any]) -> int:
        with db as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO analysis_records (
                symbol, timestamp, current_price, price_change_24h,
                has_trading_opportunity, signal_count, triggered_signals,
                trend_direction, confidence, support_level, resistance_level,
                stop_loss, target_price, suggested_position, full_analysis
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                data.get('symbol'), data.get('timestamp', datetime.now()),
                data.get('current_price'), data.get('price_change_24h'),
                data.get('has_trading_opportunity'), data.get('signal_count'),
                data.get('triggered_signals'), data.get('trend_direction'),
                data.get('confidence'), data.get('support_level'),
                data.get('resistance_level'), data.get('stop_loss'),
                data.get('target_price'), data.get('suggested_position'),
                data.get('full_analysis')))
            return cursor.lastrowid
    
    @staticmethod
    def get_recent(db: Database, symbol: str, limit: int = 10):
        with db as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM analysis_records 
                WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?""", (symbol, limit))
            return cursor.fetchall()


class SignalRecord:
    @staticmethod
    def create(db: Database, analysis_id: int, signals: list):
        with db as conn:
            cursor = conn.cursor()
            for signal in signals:
                cursor.execute("""INSERT INTO signal_records (
                    analysis_id, symbol, timestamp, signal_type, signal_strength, 
                    signal_value, signal_description) VALUES (?, ?, ?, ?, ?, ?, ?)""", (
                    analysis_id, signal.get('symbol'), signal.get('timestamp', datetime.now()),
                    signal.get('type'), signal.get('strength'),
                    signal.get('value'), signal.get('description')))


class PriceRecord:
    @staticmethod
    def create(db: Database, data: Dict[str, Any]):
        with db as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO price_records (
                symbol, timestamp, price, volume_24h, funding_rate
            ) VALUES (?, ?, ?, ?, ?)""", (
                data.get('symbol'), data.get('timestamp', datetime.now()),
                data.get('price'), data.get('volume_24h'), data.get('funding_rate')))


class SignalPerformance:
    @staticmethod
    def create(db: Database, analysis_id: int, symbol: str, entry_price: float, entry_time: datetime):
        with db as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO signal_performance (
                analysis_id, symbol, entry_price, entry_time
            ) VALUES (?, ?, ?, ?)""", (analysis_id, symbol, entry_price, entry_time))
            return cursor.lastrowid
    
    @staticmethod
    def update_performance(db: Database, performance_id: int, data: Dict[str, Any]):
        with db as conn:
            cursor = conn.cursor()
            update_fields = []
            values = []
            for field in ['price_1h', 'price_4h', 'price_24h', 
                         'return_1h', 'return_4h', 'return_24h',
                         'hit_target', 'hit_stop_loss']:
                if field in data:
                    update_fields.append(f"{field} = ?")
                    values.append(data[field])
            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                values.append(performance_id)
                query = f"UPDATE signal_performance SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, values)


class ProcessedNews:
    """已处理新闻记录"""

    @staticmethod
    def create(db: Database, symbol: str, news_id: str, title: str, source: str, published_time: int, sentiment: str) -> bool:
        """
        记录已处理的新闻

        Returns:
            bool: True表示新新闻已记录，False表示新闻已存在
        """
        try:
            with db as conn:
                cursor = conn.cursor()
                cursor.execute("""INSERT OR IGNORE INTO processed_news
                    (symbol, news_id, title, source, published_time, sentiment)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (symbol, news_id, title, source, published_time, sentiment))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"记录新闻失败: {e}")
            return False

    @staticmethod
    def is_processed(db: Database, symbol: str, news_id: str) -> bool:
        """检查新闻是否已处理"""
        with db as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT COUNT(*) as count FROM processed_news
                WHERE symbol = ? AND news_id = ?""", (symbol, news_id))
            return cursor.fetchone()['count'] > 0

    @staticmethod
    def get_latest_timestamp(db: Database, symbol: str) -> int:
        """获取最新处理的新闻时间戳"""
        with db as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT MAX(published_time) as latest FROM processed_news
                WHERE symbol = ?""", (symbol,))
            result = cursor.fetchone()['latest']
            return result if result else 0

    @staticmethod
    def cleanup_old_news(db: Database, days: int = 7):
        """清理旧新闻记录"""
        from datetime import datetime, timedelta
        cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp())
        with db as conn:
            cursor = conn.cursor()
            cursor.execute("""DELETE FROM processed_news WHERE published_time < ?""", (cutoff_time,))
            deleted = cursor.rowcount
            if deleted > 0:
                logger.info(f"清理了 {deleted} 条旧新闻记录")
