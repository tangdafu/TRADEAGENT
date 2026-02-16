import os
from langchain_anthropic import ChatAnthropic
from loguru import logger
from config.settings import settings
from .prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT_TEMPLATE


class TradingAgent:
    """交易智能体 - 使用 LangChain + Claude 进行市场分析"""

    def __init__(self):
        """初始化交易智能体"""
        logger.info("初始化交易智能体...")

        # 验证API密钥
        api_key = settings.get_llm_api_key()
        if not api_key:
            raise ValueError("LLM_API_KEY 或 ANTHROPIC_API_KEY 环境变量未设置")

        # 关键：在创建 ChatAnthropic 之前清除冲突的环境变量
        # 这样 LangChain 就不会自动检测到多个 API 密钥
        env_vars_to_clear = ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CCH_API_KEY"]
        cleared_vars = {}
        for var in env_vars_to_clear:
            if var in os.environ:
                cleared_vars[var] = os.environ.pop(var)
                logger.debug(f"临时清除环境变量: {var}")

        try:
            # 初始化 LangChain 的 ChatAnthropic
            llm_kwargs = {
                "model": settings.MODEL_NAME,
                "api_key": api_key,  # 显式传递 API 密钥
                "temperature": settings.TEMPERATURE,
                "max_tokens": 4096,
            }

            # 如果配置了自定义 API 地址，添加到参数中
            if settings.LLM_API_BASE_URL:
                logger.info(f"使用自定义 API 地址: {settings.LLM_API_BASE_URL}")
                llm_kwargs["base_url"] = settings.LLM_API_BASE_URL

            self.llm = ChatAnthropic(**llm_kwargs)

        finally:
            # 恢复环境变量（如果需要的话）
            for var, value in cleared_vars.items():
                os.environ[var] = value

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

        # 在调用时也需要清除环境变量
        # 因为 LangChain 的底层 Anthropic 客户端会在每次调用时检查环境变量
        env_vars_to_clear = ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CCH_API_KEY"]
        cleared_vars = {}
        for var in env_vars_to_clear:
            if var in os.environ:
                cleared_vars[var] = os.environ.pop(var)

        try:
            # 格式化用户消息
            user_message = ANALYSIS_PROMPT_TEMPLATE.format(market_data=market_data)

            # 使用 LangChain 的 invoke 方法
            # 传递 system 和 user 消息
            from langchain_core.messages import SystemMessage, HumanMessage

            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_message)
            ]

            response = self.llm.invoke(messages)

            # 提取文本内容
            analysis_result = response.content

            logger.info("AI分析完成")
            return analysis_result

        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
            raise
        finally:
            # 恢复环境变量
            for var, value in cleared_vars.items():
                os.environ[var] = value
