"""
交易智能体 LangGraph 工作流
使用 LangGraph 实现并行数据采集和状态管理
"""
from typing import TypedDict, Optional, Dict, Any, List, Annotated
from langgraph.graph import StateGraph, END
from loguru import logger
import operator

from src.data_collectors.funding_rate import FundingRateCollector
from src.data_collectors.kline_volume import KlineVolumeCollector
from src.data_collectors.liquidation import LiquidationCollector
from src.data_collectors.news_sentiment import NewsSentimentCollector
from src.analyzers.factor_analyzer import FactorAnalyzer
from src.agent.trading_agent import TradingAgent


class TradingState(TypedDict):
    """交易分析状态"""
    symbol: str
    verbose: bool

    # 数据采集结果
    funding_rate: Optional[Dict[str, Any]]
    kline_volume: Optional[Dict[str, Any]]
    liquidation: Optional[Dict[str, Any]]
    news_sentiment: Optional[Dict[str, Any]]

    # 处理结果
    formatted_data: Optional[str]
    analysis_result: Optional[str]

    # 错误追踪 - 使用 Annotated 支持并行更新
    errors: Annotated[List[str], operator.add]


# ============ 数据采集节点 ============

def collect_funding_rate_node(state: TradingState) -> Dict[str, Any]:
    """采集资金费率数据节点"""
    logger.info("节点: 采集资金费率数据")
    try:
        collector = FundingRateCollector()
        data = collector.collect(state["symbol"])
        logger.info("✓ 资金费率数据采集完成")
        return {"funding_rate": data, "errors": []}
    except Exception as e:
        error_msg = f"资金费率采集失败: {str(e)}"
        logger.error(error_msg)
        return {"funding_rate": None, "errors": [error_msg]}


def collect_kline_node(state: TradingState) -> Dict[str, Any]:
    """采集K线数据节点"""
    logger.info("节点: 采集K线数据")
    try:
        collector = KlineVolumeCollector()
        data = collector.collect(state["symbol"])
        logger.info("✓ K线数据采集完成")
        return {"kline_volume": data, "errors": []}
    except Exception as e:
        error_msg = f"K线数据采集失败: {str(e)}"
        logger.error(error_msg)
        return {"kline_volume": None, "errors": [error_msg]}


def collect_liquidation_node(state: TradingState) -> Dict[str, Any]:
    """采集爆仓数据节点"""
    logger.info("节点: 采集爆仓数据")
    try:
        collector = LiquidationCollector()
        data = collector.collect(state["symbol"])
        logger.info("✓ 爆仓数据采集完成")
        return {"liquidation": data, "errors": []}
    except Exception as e:
        error_msg = f"爆仓数据采集失败: {str(e)}"
        logger.error(error_msg)
        return {"liquidation": None, "errors": [error_msg]}


def collect_news_node(state: TradingState) -> Dict[str, Any]:
    """采集消息面数据节点"""
    logger.info("节点: 采集消息面数据")
    try:
        collector = NewsSentimentCollector()
        data = collector.collect(state["symbol"])
        logger.info("✓ 消息面数据采集完成")
        return {"news_sentiment": data, "errors": []}
    except Exception as e:
        error_msg = f"消息面数据采集失败: {str(e)}"
        logger.error(error_msg)
        return {"news_sentiment": None, "errors": [error_msg]}


# ============ 数据处理节点 ============

def format_data_node(state: TradingState) -> Dict[str, Any]:
    """格式化数据节点"""
    logger.info("节点: 格式化数据")
    try:
        # 检查是否有关键数据
        if not state["funding_rate"] or not state["kline_volume"]:
            raise ValueError("缺少关键数据（资金费率或K线数据）")

        # 构建分析数据
        analysis_data = {
            "symbol": state["symbol"],
            "funding_rate": state["funding_rate"],
            "kline_volume": state["kline_volume"],
            "liquidation": state["liquidation"] or {},
            "news_sentiment": state["news_sentiment"] or {},
        }

        # 格式化为LLM可读文本
        analyzer = FactorAnalyzer()
        formatted_text = analyzer.format_for_llm(analysis_data)

        if state["verbose"]:
            logger.info("格式化数据预览:")
            logger.info(formatted_text[:500] + "...")

        logger.info("✓ 数据格式化完成")
        return {"formatted_data": formatted_text, "errors": []}
    except Exception as e:
        error_msg = f"数据格式化失败: {str(e)}"
        logger.error(error_msg)
        return {"formatted_data": None, "errors": [error_msg]}


def ai_analysis_node(state: TradingState) -> Dict[str, Any]:
    """AI分析节点"""
    logger.info("节点: AI分析")
    try:
        if not state["formatted_data"]:
            raise ValueError("没有可用的格式化数据")

        agent = TradingAgent()
        result = agent.analyze(state["formatted_data"])
        logger.info("✓ AI分析完成")
        return {"analysis_result": result, "errors": []}
    except Exception as e:
        error_msg = f"AI分析失败: {str(e)}"
        logger.error(error_msg)
        return {"analysis_result": None, "errors": [error_msg]}


# ============ 构建工作流图 ============

def create_trading_graph():
    """创建交易分析工作流图"""

    # 创建状态图
    workflow = StateGraph(TradingState)

    # 添加数据采集节点（这些节点可以并行执行）
    workflow.add_node("collect_funding_rate", collect_funding_rate_node)
    workflow.add_node("collect_kline", collect_kline_node)
    workflow.add_node("collect_liquidation", collect_liquidation_node)
    workflow.add_node("collect_news", collect_news_node)

    # 添加数据处理节点
    workflow.add_node("format_data", format_data_node)
    workflow.add_node("ai_analysis", ai_analysis_node)

    # 设置入口点 - 从4个数据采集节点开始（并行执行）
    workflow.set_entry_point("collect_funding_rate")
    workflow.set_entry_point("collect_kline")
    workflow.set_entry_point("collect_liquidation")
    workflow.set_entry_point("collect_news")

    # 所有数据采集完成后，进入格式化节点
    workflow.add_edge("collect_funding_rate", "format_data")
    workflow.add_edge("collect_kline", "format_data")
    workflow.add_edge("collect_liquidation", "format_data")
    workflow.add_edge("collect_news", "format_data")

    # 格式化完成后，进入AI分析
    workflow.add_edge("format_data", "ai_analysis")

    # AI分析完成后，结束
    workflow.add_edge("ai_analysis", END)

    # 编译工作流
    app = workflow.compile()

    return app


def run_trading_analysis(symbol: str, verbose: bool = False) -> Dict[str, Any]:
    """
    运行交易分析工作流

    Args:
        symbol: 交易对符号 (如 BTCUSDT)
        verbose: 是否输出详细信息

    Returns:
        包含分析结果的字典
    """
    logger.info(f"启动 LangGraph 工作流分析: {symbol}")

    # 创建工作流
    app = create_trading_graph()

    # 初始化状态
    initial_state: TradingState = {
        "symbol": symbol,
        "verbose": verbose,
        "funding_rate": None,
        "kline_volume": None,
        "liquidation": None,
        "news_sentiment": None,
        "formatted_data": None,
        "analysis_result": None,
        "errors": [],
    }

    # 执行工作流
    logger.info("开始执行工作流...")
    final_state = app.invoke(initial_state)

    # 检查错误
    if final_state["errors"]:
        logger.warning(f"工作流执行过程中出现 {len(final_state['errors'])} 个错误:")
        for error in final_state["errors"]:
            logger.warning(f"  - {error}")

    logger.info("工作流执行完成")

    return final_state
