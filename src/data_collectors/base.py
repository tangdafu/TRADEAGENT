from abc import ABC, abstractmethod
import time
from typing import Any, Dict
from loguru import logger
from config.settings import settings


class BaseCollector(ABC):
    """数据采集器基类"""

    def __init__(self):
        self.max_retries = settings.MAX_RETRIES
        self.retry_delay = settings.RETRY_DELAY

    def _retry_on_error(self, func, *args, **kwargs) -> Any:
        """带重试机制的函数调用"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(
                        f"采集失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}"
                    )
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"采集最终失败: {str(e)}")
                    raise

    @abstractmethod
    def collect(self, symbol: str) -> Dict[str, Any]:
        """采集数据，子类必须实现"""
        pass
