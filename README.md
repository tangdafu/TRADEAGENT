# 🤖 加密货币交易智能体系统

基于 LangChain、LangGraph 和 Claude AI 的智能加密货币市场分析系统，支持实时数据采集、智能行情预判和AI驱动的交易建议。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://www.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 目录

- [核心特性](#-核心特性)
- [系统架构](#-系统架构)
- [快速开始](#-快速开始)
- [使用指南](#-使用指南)
- [配置说明](#-配置说明)
- [功能详解](#-功能详解)
- [项目结构](#-项目结构)
- [常见问题](#-常见问题)
- [更新日志](#-更新日志)
- [许可证](#-许可证)

---

## ✨ 核心特性

### 🚀 高性能数据采集
- **并行采集** - 4个数据源同时采集，速度提升3-4倍
- **多维度数据** - 资金费率、K线、市场压力、新闻情绪四大核心因子
- **实时更新** - 支持定时监控，自动获取最新市场数据

### 🎯 智能行情预判
- **多因子信号检测** - 基于5种信号的综合判断
- **阈值过滤** - 只在有交易机会时调用AI，节省API成本
- **可配置规则** - 灵活的阈值配置，适应不同交易策略

### 🤖 AI驱动分析
- **Claude AI** - 使用最先进的AI模型进行深度分析
- **结构化输出** - 包含趋势判断、风险提示、交易建议
- **完整策略** - 详细的入场、止损、目标位建议

### 💾 数据持久化
- **SQLite数据库** - 自动保存所有分析结果
- **历史查询** - 支持查询历史分析记录和统计
- **信号追踪** - 追踪信号表现和准确率

### 📱 智能告警
- **飞书推送** - 检测到交易机会时自动推送通知
- **完整策略** - 推送包含AI的详细交易策略
- **移动友好** - 手机上也能查看完整分析

### 🔧 高度可配置
- **灵活配置** - 支持自定义阈值、间隔、监控币种
- **详细日志** - 完整的决策过程记录，支持回溯分析
- **易于扩展** - 模块化设计，易于添加新功能

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        数据采集层（并行）                          │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  资金费率     │   K线数据     │  市场压力     │   消息面数据       │
│  Funding Rate│  Kline/Volume│  Liquidation │  News Sentiment   │
└──────────────┴──────────────┴──────────────┴───────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         行情预判层                                │
│  • 5种信号检测（资金费率/价格/成交量/市场压力/新闻）                │
│  • 阈值过滤（默认需2个信号）                                       │
│  • 智能触发决策                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        数据格式化层                               │
│  • 整合多维度数据                                                 │
│  • 格式化为LLM可读文本                                            │
│  • 生成结构化分析输入                                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      AI分析层（条件触发）                          │
│  • Claude AI 深度分析                                            │
│  • 市场趋势判断                                                   │
│  • 风险提示                                                       │
│  • 交易建议                                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      持久化 & 告警层                              │
│  • SQLite数据库保存                                              │
│  • 飞书告警推送（含完整AI策略）                                   │
│  • 历史数据查询                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**工作流说明：**
1. **数据采集**：4个节点并行采集市场数据（3-4x速度提升）
2. **行情预判**：基于多因子信号检测，判断是否有交易机会
3. **数据格式化**：将原始数据整合并格式化为LLM输入
4. **AI分析**：仅在检测到交易机会时调用（节省API成本）
5. **持久化 & 告警**：保存结果并推送飞书通知

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- pip 包管理器
- 稳定的网络连接

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd tradeAgent

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# LLM配置（必需）
LLM_API_BASE_URL=https://your-api-endpoint.com
LLM_API_KEY=sk-your-api-key
MODEL_NAME=claude-sonnet-4-6

# 飞书告警（可选）
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/your_webhook_token
```

### 4. 运行测试

```bash
# 单次分析
python src/main.py --symbol BTCUSDT

# 查看帮助
python src/main.py --help
```

---

## 📖 使用指南

### 单次分析模式

适用于临时查看某个币种的市场分析。

```bash
# 基础分析
python src/main.py --symbol BTCUSDT

# 详细输出（显示原始数据）
python src/main.py --symbol BTCUSDT --verbose

# 保存到数据库
python src/main.py --symbol BTCUSDT --save

# 分析其他币种
python src/main.py --symbol ETHUSDT
python src/main.py --symbol SOLUSDT
```

**输出示例：**
```
【数据采集中】正在并行采集 BTCUSDT 的市场数据...

======================================================================
                    BTC/USDT 市场分析报告
======================================================================

【核心观点】
当前BTC处于震荡偏空阶段，建议轻仓做空或观望...

【技术分析】
1. 价格在$64,800-$65,900区间震荡
2. 成交量萎缩，市场犹豫情绪明显
...

【交易策略】
建议仓位: 轻仓(10-15%)
入场价: $64,800-$65,200
止损位: $66,000
目标位: $63,200
```

### 监控模式

适用于24/7自动监控，检测到交易机会时自动推送飞书通知。

```bash
# 监控单个币种，每15分钟分析一次
python src/main.py --symbols BTCUSDT --interval 15

# 监控多个币种
python src/main.py --symbols BTCUSDT ETHUSDT SOLUSDT --interval 15

# 高频监控（每5分钟）
python src/main.py --symbols BTCUSDT --interval 5

# 详细输出模式
python src/main.py --symbols BTCUSDT --interval 15 --verbose
```

**监控输出示例：**
```
======================================================================
🔄 监控模式已启动
📊 监控币种: BTCUSDT, ETHUSDT
⏰ 监控间隔: 15 分钟
💾 自动保存: 开启
📱 飞书告警: 开启

按 Ctrl+C 停止监控
======================================================================

[2026-03-01 01:00:00] 分析 BTCUSDT (第 1 次)
======================================================================

✅ 检测到交易机会！已发送告警（含完整AI策略）

⏰ 下次分析时间: 15 分钟后
```

**停止监控：**
- 按 `Ctrl+C` 优雅退出
- 系统会完成当前分析后停止

---

## ⚙️ 配置说明

### 环境变量配置

#### LLM配置（必需）

```bash
# API端点
LLM_API_BASE_URL=https://your-api-endpoint.com

# API密钥
LLM_API_KEY=sk-your-api-key

# 模型名称
MODEL_NAME=claude-sonnet-4-6
```

#### 飞书告警配置（可选）

```bash
# 飞书Webhook地址
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/your_webhook_token
```

**配置步骤：**

1. 在飞书群聊中点击右上角**设置**
2. 选择 **群机器人** → **添加机器人** → **自定义机器人**
3. 设置机器人名称（如：交易信号助手）
4. 复制Webhook地址
5. 添加到 `.env` 文件

### 信号检测阈值配置

编辑 `config/settings.py` 自定义阈值：

```python
# 资金费率阈值
FUNDING_RATE_THRESHOLD = 0.05  # 5%

# 价格变化阈值
PRICE_CHANGE_THRESHOLD = 2.0  # 2%

# 成交量变化阈值
VOLUME_CHANGE_THRESHOLD = 1.5  # 1.5倍

# 最小信号数量
MIN_SIGNAL_COUNT = 2  # 至少2个信号才触发AI分析
```

---

## 🎯 功能详解

### 1. 并行数据采集

系统使用 LangGraph 实现4个数据源的并行采集：

- **资金费率** - 反映多空力量对比
- **K线数据** - 价格走势和成交量
- **市场压力** - 爆仓数据和持仓量
- **消息面** - 新闻情绪和社交媒体

**优势：**
- 速度提升3-4倍
- 数据更全面
- 决策更准确

### 2. 智能行情预判

基于5种信号的综合判断：

1. **资金费率异常** - 费率过高或过低
2. **价格剧烈波动** - 24h涨跌幅超过阈值
3. **成交量异常** - 成交量激增或萎缩
4. **市场压力** - 大额爆仓或持仓异常
5. **新闻情绪** - 消息面积极或消极

**触发条件：**
- 默认需要至少2个信号同时触发
- 可自定义阈值和最小信号数量

**优势：**
- 节省API成本（只在有机会时调用AI）
- 提高分析质量（过滤噪音）
- 减少告警疲劳

### 3. AI深度分析

使用 Claude AI 进行深度市场分析：

**分析内容：**
- 核心观点
- 技术分析
- 资金面分析
- 详细交易策略
- 风险提示
- 替代方案
- 总结建议

**输出格式：**
- 结构化文本
- 易于阅读
- 包含具体数值

### 4. 数据持久化

所有分析结果可选保存到SQLite数据库：

**保存内容：**
- 分析时间、交易对、当前价格
- 触发信号、AI分析结果
- 交易建议（仓位、止损、目标）

**当前状态：**
- ✅ 数据保存功能完整
- ⏳ 查询功能已实现但未集成到CLI
- 🔮 未来可扩展：准确率统计、策略优化、Web可视化

**使用方式：**
- 监控模式：自动保存所有分析
- 单次分析：使用 `--save` 参数保存
- 手动查询：通过Python脚本或SQLite工具

详细说明：[docs/DATABASE_GUIDE.md](docs/DATABASE_GUIDE.md)

### 5. 飞书智能告警

检测到交易机会时自动推送飞书通知：

**消息内容：**
- 基础信息（价格、涨跌、趋势、信心度）
- 触发信号列表
- 交易建议（仓位、止损、目标）
- **完整AI策略**（核心观点、技术分析、风险提示等）

**消息格式：**
- 精美的卡片式展示
- 分栏布局，易于阅读
- 移动端友好

**优势：**
- 一条消息包含所有决策信息
- 无需切换到电脑查看
- 随时随地做出交易决策

---

## 📁 项目结构

```
tradeAgent/
├── config/                      # 配置文件
│   ├── settings.py             # 系统配置
│   └── prompts.py              # AI提示词
├── src/
│   ├── data_collectors/        # 数据采集器
│   │   ├── funding_rate.py    # 资金费率
│   │   ├── kline_volume.py    # K线数据
│   │   ├── liquidation.py     # 市场压力
│   │   └── news_sentiment.py  # 消息面
│   ├── analyzers/              # 分析器
│   │   └── market_signal_detector.py  # 信号检测
│   ├── workflow/               # 工作流
│   │   └── trading_graph.py   # LangGraph工作流
│   ├── database/               # 数据库
│   │   ├── models.py          # 数据模型
│   │   └── repository.py      # 数据仓库
│   ├── scheduler/              # 调度器
│   │   ├── task_scheduler.py  # 任务调度
│   │   └── alert_manager.py   # 告警管理
│   ├── utils/                  # 工具函数
│   │   ├── logger.py          # 日志配置
│   │   └── formatters.py      # 格式化工具
│   └── main.py                 # 主程序入口
├── tests/                       # 测试脚本
│   ├── test_new_features.py   # 功能测试
│   ├── test_feishu.py         # 飞书测试
│   └── test_full_analysis.py  # 完整策略测试
├── docs/                        # 文档
│   ├── USAGE_GUIDE.md         # 使用指南
│   └── FEISHU_TROUBLESHOOTING.md  # 故障排查
├── logs/                        # 日志文件
├── data/                        # 数据文件
│   └── trading_agent.db       # SQLite数据库
├── .env.example                # 环境变量示例
├── requirements.txt            # 依赖列表
├── CHANGELOG.md                # 更新日志
└── README.md                   # 项目说明
```

---

## ❓ 常见问题

### Q1: 如何获取LLM API密钥？

**回答：**
- 本项目支持任何兼容OpenAI格式的API
- 推荐使用Claude API（通过第三方代理）
- 配置 `LLM_API_BASE_URL` 和 `LLM_API_KEY`

### Q2: 飞书没有收到通知？

**排查步骤：**

1. 检查Webhook配置是否正确
2. 确认机器人已添加到群聊
3. 运行测试脚本：`python tests/test_feishu.py`
4. 查看日志文件：`logs/trade_agent.log`

详细排查指南：`docs/FEISHU_TROUBLESHOOTING.md`

### Q3: 监控模式没有发送告警？

**原因：**
- 监控模式只在检测到交易机会时才发送告警
- 如果市场平静，不会触发告警

**验证方法：**
- 运行测试脚本强制发送：`python tests/test_full_analysis.py`
- 查看日志确认是否检测到交易机会
- 降低信号阈值（编辑 `config/settings.py`）

### Q4: 如何自定义信号阈值？

**步骤：**

1. 编辑 `config/settings.py`
2. 修改相关阈值参数
3. 重启程序

```python
# 示例：降低资金费率阈值
FUNDING_RATE_THRESHOLD = 0.03  # 从5%降到3%
```

### Q5: 数据库文件在哪里？

**位置：**
- `data/trading_agent.db`
- 首次运行时自动创建
- 使用SQLite，无需额外配置

### Q6: 如何查看历史分析记录？

**方法：**

```python
from src.database import AnalysisRepository

repo = AnalysisRepository()

# 查询最近10条记录
records = repo.get_recent_analyses("BTCUSDT", limit=10)

# 查询统计信息
stats = repo.get_signal_statistics("BTCUSDT", days=7)
```

### Q7: 支持哪些交易对？

**支持：**
- 所有币安合约交易对
- 格式：`BTCUSDT`, `ETHUSDT`, `SOLUSDT` 等
- 必须是USDT结算的合约

### Q8: 如何停止监控模式？

**方法：**
- 按 `Ctrl+C` 优雅退出
- 系统会完成当前分析后停止
- 不会丢失数据


### Q9: 数据库有什么用？

**当前状态：**
- 数据库主要用于**数据积累**
- 监控模式自动保存所有分析结果
- 查询功能已实现但未集成到CLI

**使用场景：**
- 长期运行积累历史数据
- 手动查询历史分析记录
- 为未来的策略优化提供数据基础

**手动查询示例：**
```python
from src.database import AnalysisRepository

repo = AnalysisRepository()
records = repo.get_recent_analyses("BTCUSDT", limit=10)
stats = repo.get_signal_statistics("BTCUSDT", days=7)
```

**未来扩展：**
- 准确率统计
- 策略优化
- Web可视化
- 回测功能

详细说明：[docs/DATABASE_GUIDE.md](docs/DATABASE_GUIDE.md)

------

## 📝 更新日志

### v2.1.0 - 2026-03-01

**新增功能：**
- ✅ 飞书告警优化，推送包含完整AI交易策略
- ✅ 详细展示核心观点、技术分析、资金面分析
- ✅ 包含详细交易策略、风险提示、替代方案
- ✅ 一条消息包含所有决策信息

**修复：**
- ✅ 修复监控模式数据保存错误
- ✅ 修复飞书告警配置加载问题

### v2.0.0 - 2024-03-01

**新增功能：**
- ✅ 数据持久化（SQLite数据库）
- ✅ 定时监控系统
- ✅ 飞书告警推送
- ✅ 历史数据查询
- ✅ 信号追踪统计

**改进：**
- ✅ 统一入口（单次分析 + 监控模式）
- ✅ 优化代码结构
- ✅ 完善文档

### v1.0.0 - 初始版本

- ✅ 并行数据采集
- ✅ 智能行情预判
- ✅ AI驱动分析
- ✅ 多维度数据整合

详细更新日志：[CHANGELOG.md](CHANGELOG.md)

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📄 许可证

MIT License

---

## ⚠️ 免责声明

**本项目仅供学习和研究使用，不构成任何投资建议。**

- 加密货币交易风险极高，请谨慎决策
- 建议在模拟环境充分测试后再考虑实盘使用
- 过去的表现不代表未来的结果
- 任何交易决策请自行承担风险

---

## 📞 联系方式

- 项目地址：[GitHub Repository]
- 问题反馈：[Issues]
- 文档：[docs/](docs/)

---

**⭐ 如果这个项目对你有帮助，请给个Star！**


