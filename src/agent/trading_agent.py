from typing import Dict, Any
from langchain_anthropic import ChatAnthropic
from loguru import logger
from config.settings import settings
from .prompts import get_analysis_prompt


class TradingAgent:
    """交易智能体 - 使用Claude进行市场分析"""

    def __init__(self):
        """初始化交易智能体"""
        logger.info("初始化交易智能体...")

        # 验证API密钥
        api_key = settings.get_llm_api_key()
        if not api_key:
            raise ValueError("LLM_API_KEY 或 ANTHROPIC_API_KEY 环境变量未设置")

        # 初始化Claude模型
        llm_kwargs = {
            "model": settings.MODEL_NAME,
            "api_key": api_key,
            "temperature": settings.TEMPERATURE,
        }

        # 如果配置了自定义 API 地址，添加到参数中
        if settings.LLM_API_BASE_URL:
            logger.info(f"使用自定义 API 地址: {settings.LLM_API_BASE_URL}")
            llm_kwargs["base_url"] = settings.LLM_API_BASE_URL

        self.llm = ChatAnthropic(**llm_kwargs)

        # 获取Prompt模板
        self.prompt = get_analysis_prompt()

        # 创建分析链
        self.chain = self.prompt | self.llm

        if settings.LLM_API_BASE_URL:
            logger.info(f"交易智能体初始化完成 (模型: {settings.MODEL_NAME}) - {settings.LLM_API_BASE_URL}")
        else:
            logger.info(f"交易智能体初始化完成 (模型: {settings.MODEL_NAME})")

    def analyze(self, market_data: str) -> str:
        """
        分析市场数据并给出交易建议

        Args:
            market_data: 格式化的市场数据文本

        Returns:
            Claude的分析结果
        """
        logger.info("开始AI分析...")

        try:
            # 调用Claude进行分析
            response = self.chain.invoke({"market_data": market_data})

            # 提取文本内容
            if hasattr(response, "content"):
                analysis_result = response.content
            else:
                analysis_result = str(response)

            logger.info("AI分析完成")
            return analysis_result

        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
            raise
