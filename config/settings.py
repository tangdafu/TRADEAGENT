import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings:
    """应用配置"""

    # LLM API 配置
    LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # 模型配置
    MODEL_NAME = os.getenv("MODEL_NAME", "claude-sonnet-4-5-20250929")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))

    # 交易配置
    SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
    SYMBOLS = ["BTCUSDT", "ETHUSDT"]

    # Binance API 配置
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")

    # 消息面数据API配置
    CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY", "")
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

    # 数据采集配置
    FUNDING_RATE_EXTREME_THRESHOLD = 0.001  # ±0.1%
    LIQUIDATION_THRESHOLD = 100000  # 100,000 USDT
    KLINE_INTERVAL = "1h"
    KLINE_LIMIT = 24  # 24小时

    # 行情预判配置
    MARKET_SIGNAL_DETECTION_ENABLED = os.getenv("MARKET_SIGNAL_DETECTION_ENABLED", "true").lower() == "true"
    MIN_SIGNAL_COUNT = int(os.getenv("MIN_SIGNAL_COUNT", "2"))  # 最少触发信号数

    # 资金费率信号阈值
    FUNDING_RATE_CHANGE_THRESHOLD = float(os.getenv("FUNDING_RATE_CHANGE_THRESHOLD", "0.0005"))  # 0.05%

    # 价格波动信号阈值
    PRICE_CHANGE_THRESHOLD = float(os.getenv("PRICE_CHANGE_THRESHOLD", "5.0"))  # 5%

    # 成交量信号阈值
    VOLUME_SURGE_RATIO = float(os.getenv("VOLUME_SURGE_RATIO", "2.0"))  # 2倍均值

    # 爆仓信号阈值
    LARGE_LIQUIDATION_COUNT_THRESHOLD = int(os.getenv("LARGE_LIQUIDATION_COUNT_THRESHOLD", "3"))  # 3笔大额爆仓

    # 消息面情绪阈值
    NEWS_SENTIMENT_THRESHOLD = float(os.getenv("NEWS_SENTIMENT_THRESHOLD", "0.5"))  # 情绪得分±0.5

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = "logs"

    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # 秒

    @classmethod
    def validate(cls):
        """验证必需的配置"""
        api_key = cls.get_llm_api_key()
        if not api_key:
            raise ValueError("LLM_API_KEY 或 ANTHROPIC_API_KEY 环境变量未设置")

    @classmethod
    def get_llm_api_key(cls):
        """获取 LLM API 密钥"""
        return cls.LLM_API_KEY if cls.LLM_API_KEY else cls.ANTHROPIC_API_KEY


# 创建全局配置实例
settings = Settings()
