"""
告警通知模块
支持多种通知方式：飞书、邮件、控制台
"""
import os
import requests
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        """初始化告警管理器"""
        self.feishu_enabled = False
        self.email_enabled = False
        
        # 从环境变量加载配置
        self._load_config()
    
    def _load_config(self):
        """加载告警配置"""
        # 飞书配置
        self.feishu_webhook = os.getenv('FEISHU_WEBHOOK', '')
        
        if self.feishu_webhook:
            self.feishu_enabled = True
            logger.info("飞书告警已启用")
        
        # 邮件配置（预留）
        self.email_enabled = False
    
    def send_alert(self, symbol: str, analysis_result: Dict[str, Any], full_analysis: str = ""):
        """
        发送告警
        
        Args:
            symbol: 交易对
            analysis_result: 分析结果（结构化数据）
            full_analysis: AI完整分析文本（可选）
        """
        # 控制台输出
        self._console_alert(symbol, analysis_result)
        
        # 飞书通知
        if self.feishu_enabled:
            self._send_feishu(symbol, analysis_result, full_analysis)
        
        # 邮件通知（预留）
        if self.email_enabled:
            self._send_email(symbol, analysis_result)
    
    def send_trading_alert(self, symbol: str, analysis_result: Dict[str, Any], formatted_output: str = ""):
        """
        发送交易告警（兼容旧接口）
        
        Args:
            symbol: 交易对
            analysis_result: 分析结果
            formatted_output: 格式化输出（可选）
        """
        self.send_alert(symbol, analysis_result)
    
    def _console_alert(self, symbol: str, result: Dict[str, Any]):
        """控制台告警"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.warning("\n" + "=" * 70)
        logger.warning(f"🚨 交易信号提醒 - {symbol} - {timestamp}")
        logger.warning(f"当前价格: {result.get('current_price', 'N/A')}")
        logger.warning(f"24h涨跌: {result.get('price_change_24h', 0):.2f}%")
        logger.warning(f"趋势判断: {result.get('trend_direction', '未知')}")
        logger.warning(f"信心度: {result.get('confidence', 0)*100:.0f}%")
        logger.warning("=" * 70)
    
    def _send_feishu(self, symbol: str, result: Dict[str, Any], full_analysis: str = ""):
        """
        发送飞书消息
        
        Args:
            symbol: 交易对
            result: 分析结果
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 提取关键信息
            current_price = result.get('current_price', 'N/A')
            price_change = result.get('price_change_24h', 0)
            trend = result.get('trend_direction', '未知')
            confidence = result.get('confidence', 0)
            signals = result.get('triggered_signals', [])
            
            # 构建飞书卡片消息
            card = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": f"🚨 交易信号提醒 - {symbol}"
                        },
                        "template": "red"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": f"**⏰ 时间**: {timestamp}"
                            }
                        },
                        {
                            "tag": "hr"
                        },
                        {
                            "tag": "div",
                            "fields": [
                                {
                                    "is_short": True,
                                    "text": {
                                        "tag": "lark_md",
                                        "content": f"**💰 当前价格**\n{current_price}"
                                    }
                                },
                                {
                                    "is_short": True,
                                    "text": {
                                        "tag": "lark_md",
                                        "content": f"**📈 24h涨跌**\n{price_change:.2f}%"
                                    }
                                }
                            ]
                        },
                        {
                            "tag": "div",
                            "fields": [
                                {
                                    "is_short": True,
                                    "text": {
                                        "tag": "lark_md",
                                        "content": f"**🎯 趋势判断**\n{trend}"
                                    }
                                },
                                {
                                    "is_short": True,
                                    "text": {
                                        "tag": "lark_md",
                                        "content": f"**💪 信心度**\n{confidence*100:.0f}%"
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
            
            # 添加触发信号
            if signals:
                signals_text = "**⚡ 触发信号**\n"
                for signal in signals:
                    signals_text += f"• {signal}\n"
                
                card["card"]["elements"].append({
                    "tag": "hr"
                })
                card["card"]["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": signals_text
                    }
                })
            
            # 添加交易建议
            if result.get('suggested_position') or result.get('stop_loss') or result.get('target_price'):
                card["card"]["elements"].append({
                    "tag": "hr"
                })
                
                advice_fields = []
                if result.get('suggested_position'):
                    advice_fields.append({
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**💡 建议仓位**\n{result.get('suggested_position')}"
                        }
                    })
                
                if result.get('stop_loss'):
                    advice_fields.append({
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**🛑 止损位**\n{result.get('stop_loss')}"
                        }
                    })
                
                if result.get('target_price'):
                    advice_fields.append({
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**🎯 目标位**\n{result.get('target_price')}"
                        }
                    })
                
                if advice_fields:
                    card["card"]["elements"].append({
                        "tag": "div",
                        "fields": advice_fields
                    })
            
            # 添加AI完整分析（如果有）
            if full_analysis:
                card["card"]["elements"].append({
                    "tag": "hr"
                })
                card["card"]["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "**📊 AI交易策略**"
                    }
                })
                
                # 截取分析文本（飞书卡片有长度限制，最多3000字符）
                analysis_text = full_analysis[:3000] if len(full_analysis) > 3000 else full_analysis
                
                card["card"]["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": analysis_text
                    }
                })
            
            # 添加风险提示
            card["card"]["elements"].append({
                "tag": "hr"
            })
            card["card"]["elements"].append({
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "⚠️ 风险提示: 仅供参考，请谨慎决策"
                    }
                ]
            })
            
            # 发送请求
            response = requests.post(
                self.feishu_webhook,
                json=card,
                timeout=10
            )
            
            if response.status_code == 200:
                result_data = response.json()
                if result_data.get('code') == 0:
                    logger.info("飞书消息发送成功")
                else:
                    logger.error(f"飞书消息发送失败: {result_data}")
            else:
                logger.error(f"飞书消息发送失败: HTTP {response.status_code}")
        
        except Exception as e:
            logger.error(f"发送飞书消息时出错: {e}")
    
    def _send_email(self, symbol: str, result: Dict[str, Any]):
        """
        发送邮件（预留）
        
        Args:
            symbol: 交易对
            result: 分析结果
        """
        # TODO: 实现邮件发送
        pass
    
    def send_daily_report(self, statistics: Dict[str, Any]):
        """
        发送每日报告
        
        Args:
            statistics: 统计数据
        """
        if self.feishu_enabled:
            self._send_feishu_report(statistics)
        
        logger.info("每日报告已发送")
    
    def _send_feishu_report(self, stats: Dict[str, Any]):
        """发送飞书每日报告"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d')
            
            # 构建飞书卡片
            card = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": f"📊 每日交易报告 - {timestamp}"
                        },
                        "template": "blue"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "fields": [
                                {
                                    "is_short": True,
                                    "text": {
                                        "tag": "lark_md",
                                        "content": f"**总分析次数**\n{stats.get('total_analyses', 0)}"
                                    }
                                },
                                {
                                    "is_short": True,
                                    "text": {
                                        "tag": "lark_md",
                                        "content": f"**交易机会**\n{stats.get('opportunity_count', 0)}"
                                    }
                                }
                            ]
                        },
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": f"**机会率**: {stats.get('opportunity_rate', 0)*100:.1f}%"
                            }
                        }
                    ]
                }
            }
            
            # 添加趋势分布
            trend_dist = stats.get('trend_distribution', {})
            if trend_dist:
                trend_text = "**🎯 趋势分布**\n"
                for trend, count in trend_dist.items():
                    trend_text += f"• {trend}: {count}次\n"
                
                card["card"]["elements"].append({
                    "tag": "hr"
                })
                card["card"]["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": trend_text
                    }
                })
            
            # 添加平均信心度
            avg_conf = stats.get('avg_confidence', 0)
            if avg_conf:
                card["card"]["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**💪 平均信心度**: {avg_conf*100:.0f}%"
                    }
                })
            
            # 发送请求
            response = requests.post(
                self.feishu_webhook,
                json=card,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("飞书每日报告发送成功")
            else:
                logger.error(f"飞书每日报告发送失败: HTTP {response.status_code}")
        
        except Exception as e:
            logger.error(f"发送飞书每日报告时出错: {e}")


class SimpleAlert:
    """简单告警（仅控制台输出）"""
    
    @staticmethod
    def alert(symbol: str, message: str):
        """发送简单告警"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.warning(f"\n{'='*70}")
        logger.warning(f"🚨 告警 - {symbol} - {timestamp}")
        logger.warning(message)
        logger.warning(f"{'='*70}\n")




