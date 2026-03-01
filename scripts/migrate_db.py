"""
数据库迁移脚本 - 添加准确率追踪字段
"""
import sqlite3
from pathlib import Path
from loguru import logger


def migrate_database():
    """迁移数据库，添加新字段"""
    db_path = Path("data/trading_agent.db")
    
    if not db_path.exists():
        logger.info("数据库不存在，无需迁移")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 检查是否需要添加字段
        cursor.execute("PRAGMA table_info(signal_performance)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # 需要添加的字段
        new_columns = {
            'exit_price': 'REAL',
            'exit_time': 'DATETIME',
            'price_change_pct': 'REAL',
            'is_profitable': 'BOOLEAN'
        }
        
        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                logger.info(f"添加字段: {col_name}")
                cursor.execute(f"ALTER TABLE signal_performance ADD COLUMN {col_name} {col_type}")
        
        conn.commit()
        logger.info("数据库迁移完成")
        print("✅ 数据库迁移成功")
        
    except Exception as e:
        logger.error(f"数据库迁移失败: {e}")
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()
