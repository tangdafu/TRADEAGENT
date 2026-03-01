"""
工具函数模块
包含日志设置等工具函数
"""
from pathlib import Path
from config.settings import settings


def create_logs_directory():
    """创建日志目录"""
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)
