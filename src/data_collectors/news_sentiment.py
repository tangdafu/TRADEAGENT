from typing import Dict, Any, List
import requests
from loguru import logger
from .base import BaseCollector
from config.settings import settings
from datetime import datetime


class NewsSentimentCollector(BaseCollector):
    """消息面和情绪数据采集器 - 整合多个数据源"""

    def __init__(self):
        super().__init__()
        self.cryptocompare_api_key = settings.CRYPTOCOMPARE_API_KEY
        self.newsapi_key = settings.NEWSAPI_KEY

    def collect(self, symbol: str) -> Dict[str, Any]:
        """采集消息面数据"""
        logger.info(f"采集消息面数据: {symbol}")

        # 提取币种名称（去掉USDT后缀）
        coin = symbol.replace("USDT", "").replace("BUSD", "")

        def _fetch():
            # 收集各类消息面数据
            crypto_news = self._get_crypto_news(coin)
            social_sentiment = self._get_social_sentiment(coin)
            macro_news = self._get_macro_news()

            # 综合分析
            overall_sentiment = self._calculate_overall_sentiment(
                crypto_news, social_sentiment, macro_news
            )

            # 检查是否有任何可用数据
            data_available = (
                crypto_news.get("data_available", False) or
                social_sentiment.get("data_available", False) or
                macro_news.get("data_available", False)
            )

            return {
                "crypto_news": crypto_news,
                "social_sentiment": social_sentiment,
                "macro_news": macro_news,
                "overall_sentiment": overall_sentiment,
                "timestamp": datetime.now().isoformat(),
                "data_available": data_available,
            }

        return self._retry_on_error(_fetch)

    def _get_crypto_news(self, coin: str) -> Dict[str, Any]:
        """获取加密货币新闻（CryptoCompare API）"""
        try:
            if not self.cryptocompare_api_key:
                logger.warning("未配置CryptoCompare API密钥，无法获取加密货币新闻")
                return {
                    "news_count": 0,
                    "news_list": [],
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                    "sentiment_score": 0.0,
                    "data_available": False,
                }

            url = "https://min-api.cryptocompare.com/data/v2/news/"
            params = {
                "categories": coin,
                "lang": "EN",
            }
            headers = {"authorization": f"Apikey {self.cryptocompare_api_key}"}

            response = requests.get(url, params=params, headers=headers, timeout=20)
            response.raise_for_status()
            data = response.json()

            # 检查是否有数据返回（CryptoCompare API v2格式）
            if "Data" in data and data.get("Data"):
                news_items = data.get("Data", [])[:5]  # 取最新5条

                # 分析新闻情绪
                positive_count = 0
                negative_count = 0
                neutral_count = 0

                news_list = []
                for item in news_items:
                    title = item.get("title", "")
                    sentiment = self._analyze_news_sentiment(title)

                    if sentiment == "positive":
                        positive_count += 1
                    elif sentiment == "negative":
                        negative_count += 1
                    else:
                        neutral_count += 1

                    news_list.append({
                        "title": title,
                        "source": item.get("source", ""),
                        "published": item.get("published_on", 0),
                        "sentiment": sentiment,
                    })

                return {
                    "news_count": len(news_list),
                    "news_list": news_list,
                    "positive_count": positive_count,
                    "negative_count": negative_count,
                    "neutral_count": neutral_count,
                    "sentiment_score": self._calculate_sentiment_score(
                        positive_count, negative_count, neutral_count
                    ),
                    "data_available": True,
                }
            else:
                logger.warning(f"CryptoCompare API返回失败: {data.get('Message', 'Unknown error')}")
                return {
                    "news_count": 0,
                    "news_list": [],
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                    "sentiment_score": 0.0,
                    "data_available": False,
                }

        except Exception as e:
            logger.warning(f"获取加密货币新闻失败: {str(e)}")
            return {
                "news_count": 0,
                "news_list": [],
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "sentiment_score": 0.0,
                "data_available": False,
            }

    def _get_social_sentiment(self, coin: str) -> Dict[str, Any]:
        """获取社交媒体情绪（简化版 - 使用CryptoCompare社交数据）"""
        try:
            if not self.cryptocompare_api_key:
                logger.warning("未配置API密钥，无法获取社交数据")
                return {
                    "twitter_followers": 0,
                    "twitter_points": 0,
                    "reddit_subscribers": 0,
                    "reddit_active_users": 0,
                    "sentiment": "unknown",
                    "data_available": False,
                }

            url = f"https://min-api.cryptocompare.com/data/social/coin/latest"
            params = {"coinId": self._get_coin_id(coin)}
            headers = {"authorization": f"Apikey {self.cryptocompare_api_key}"}

            response = requests.get(url, params=params, headers=headers, timeout=20)
            response.raise_for_status()
            data = response.json()

            # 检查是否有数据返回
            if "Data" in data and data.get("Data"):
                social_data = data.get("Data", {})

                # 提取关键指标
                twitter_data = social_data.get("Twitter", {})
                reddit_data = social_data.get("Reddit", {})

                return {
                    "twitter_followers": twitter_data.get("followers", 0),
                    "twitter_points": twitter_data.get("Points", 0),
                    "reddit_subscribers": reddit_data.get("subscribers", 0),
                    "reddit_active_users": reddit_data.get("active_users", 0),
                    "sentiment": "neutral",  # 简化处理
                    "data_available": True,
                }
            else:
                logger.warning(f"CryptoCompare社交数据API返回失败: {data.get('Message', 'Unknown error')}")
                return {
                    "twitter_followers": 0,
                    "twitter_points": 0,
                    "reddit_subscribers": 0,
                    "reddit_active_users": 0,
                    "sentiment": "unknown",
                    "data_available": False,
                }

        except Exception as e:
            logger.warning(f"获取社交情绪失败: {str(e)}")
            return {
                "twitter_followers": 0,
                "twitter_points": 0,
                "reddit_subscribers": 0,
                "reddit_active_users": 0,
                "sentiment": "unknown",
                "data_available": False,
            }

    def _get_macro_news(self) -> Dict[str, Any]:
        """获取宏观财经新闻"""
        try:
            if not self.newsapi_key:
                logger.warning("未配置NewsAPI密钥，无法获取宏观新闻")
                return {
                    "news_count": 0,
                    "news_list": [],
                    "data_available": False,
                }

            # 使用NewsAPI获取美联储、经济相关新闻
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": "Federal Reserve OR cryptocurrency OR Bitcoin",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 5,
                "apiKey": self.newsapi_key,
            }

            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "ok":
                articles = data.get("articles", [])[:5]

                news_list = []
                for article in articles:
                    news_list.append({
                        "title": article.get("title", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "published": article.get("publishedAt", ""),
                    })

                return {
                    "news_count": len(news_list),
                    "news_list": news_list,
                    "data_available": True,
                }
            else:
                logger.warning(f"NewsAPI返回失败: {data.get('message', 'Unknown error')}")
                return {
                    "news_count": 0,
                    "news_list": [],
                    "data_available": False,
                }

        except Exception as e:
            logger.warning(f"获取宏观新闻失败: {str(e)}")
            return {
                "news_count": 0,
                "news_list": [],
                "data_available": False,
            }

    def _analyze_news_sentiment(self, title: str) -> str:
        """简单的新闻情绪分析（基于关键词）"""
        title_lower = title.lower()

        positive_keywords = [
            "surge", "rally", "bullish", "gain", "rise", "up", "high",
            "breakthrough", "adoption", "partnership", "launch", "success"
        ]
        negative_keywords = [
            "crash", "drop", "fall", "bearish", "decline", "down", "low",
            "hack", "scam", "ban", "regulation", "lawsuit", "concern"
        ]

        positive_score = sum(1 for kw in positive_keywords if kw in title_lower)
        negative_score = sum(1 for kw in negative_keywords if kw in title_lower)

        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"

    def _calculate_sentiment_score(self, positive: int, negative: int, neutral: int) -> float:
        """计算情绪得分 (-1到1之间)"""
        total = positive + negative + neutral
        if total == 0:
            return 0.0
        return (positive - negative) / total

    def _calculate_overall_sentiment(
        self, crypto_news: Dict, social: Dict, macro: Dict
    ) -> Dict[str, Any]:
        """综合计算整体市场情绪"""
        # 简化的综合评分逻辑
        news_sentiment = crypto_news.get("sentiment_score", 0)

        # 综合评分
        overall_score = news_sentiment  # 可以加权其他因素

        if overall_score > 0.3:
            sentiment = "积极"
            signal = "消息面偏多"
        elif overall_score < -0.3:
            sentiment = "消极"
            signal = "消息面偏空"
        else:
            sentiment = "中性"
            signal = "消息面中性"

        return {
            "sentiment": sentiment,
            "score": overall_score,
            "signal": signal,
        }

    def _get_coin_id(self, coin: str) -> int:
        """获取CryptoCompare的币种ID"""
        coin_ids = {
            "BTC": 1182,
            "ETH": 7605,
            "BNB": 4432,
            # 可以扩展更多
        }
        return coin_ids.get(coin, 1182)
