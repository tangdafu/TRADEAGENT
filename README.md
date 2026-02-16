# 交易智能体系统

基于LangChain和Claude的BTC/ETH合约交易智能分析系统。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API

编辑 `.env` 文件：

```env
# 第三方API地址（如果使用第三方供应商）
LLM_API_BASE_URL=https://api.asxs.top
LLM_API_KEY=sk-your-api-key

# 或使用官方Anthropic API
# ANTHROPIC_API_KEY=sk-ant-your-key
```

### 3. 运行分析

```bash
# 分析BTC
python src/main.py

# 分析ETH
python src/main.py --symbol ETHUSDT

# 详细输出（显示原始数据和工作流统计）
python src/main.py --verbose
```

**系统特性：**
- ✨ 并行采集4个数据源，速度提升3-4倍
- 📊 清晰的状态管理和错误追踪
- 🔄 自动处理节点依赖关系
- 🎯 更好的可扩展性和可维护性

## 功能特性

- 🔄 **实时数据采集** - 从币安API获取市场数据
- 📊 **多维度分析** - 资金费率、K线成交量、爆仓数据、消息面情绪
- ⚡ **并行执行** - LangGraph实现4个数据源并行采集，速度提升3-4倍
- 🤖 **AI智能分析** - 使用Claude进行深度分析
- 💡 **交易建议** - 给出具体的交易方向和风险提示
- 🎯 **状态管理** - LangGraph提供清晰的工作流状态追踪

## 核心因素

1. **资金费率** - 反映多空拥挤度
2. **K线与成交量** - 技术面分析
3. **爆仓数据** - 市场情绪指标（需配置API密钥）
4. **消息面与情绪** - 加密货币新闻、社交媒体情绪、宏观财经新闻（需配置API密钥）

## LangGraph工作流架构

系统使用LangGraph实现并行数据采集，工作流如下：

```
初始状态
    │
    ├─────┬─────┬─────┐
    │     │     │     │
    ▼     ▼     ▼     ▼
  资金  K线  爆仓  消息  (并行执行)
  费率  数据  数据  面
    │     │     │     │
    └─────┴─────┴─────┘
            │
            ▼
        格式化数据
            │
            ▼
         AI分析
            │
            ▼
          输出结果
```

**关键特性：**
- 4个数据采集节点并行执行
- 使用TypedDict进行状态管理
- 自动错误追踪和处理
- 节点间依赖关系自动管理

## 项目结构

```
src/
├── main.py                    # 主程序入口（LangGraph并行版本）
├── workflow/                  # LangGraph工作流模块
│   ├── __init__.py
│   └── trading_graph.py       # 工作流定义和节点实现
├── data_collectors/           # 数据采集模块
│   ├── base.py
│   ├── funding_rate.py
│   ├── kline_volume.py
│   ├── liquidation.py
│   └── news_sentiment.py
├── analyzers/                 # 数据分析模块
│   └── factor_analyzer.py     # 数据格式化
├── agent/                     # AI智能体
│   ├── prompts.py
│   └── trading_agent.py
└── utils/                     # 工具函数
    ├── logger.py
    └── formatters.py

config/
└── settings.py                # 配置管理

tests/                          # 测试代码
├── test_simple.py
├── test_llm_config.py
└── demo.py
```

## 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `LLM_API_BASE_URL` | API地址 | `https://api.asxs.top` |
| `LLM_API_KEY` | API密钥 | `sk-xxx` |
| `ANTHROPIC_API_KEY` | Anthropic密钥（可选） | `sk-ant-xxx` |
| `MODEL_NAME` | 模型名称 | `claude-sonnet-4-5-20250929` |
| `SYMBOL` | 交易对 | `BTCUSDT` |
| `BINANCE_API_KEY` | 币安API密钥（可选，用于爆仓数据） | `xxx` |
| `BINANCE_API_SECRET` | 币安API密钥（可选，用于爆仓数据） | `xxx` |
| `CRYPTOCOMPARE_API_KEY` | CryptoCompare密钥（可选，用于新闻和社交数据） | `xxx` |
| `NEWSAPI_KEY` | NewsAPI密钥（可选，用于宏观新闻） | `xxx` |

## 测试

```bash
# 运行系统测试
python tests/test_simple.py

# 测试LLM配置
python tests/test_llm_config.py

# 演示数据采集
python tests/demo.py
```

## 输出示例

```
╔════════════════════════════════════════════════════════════════╗
║                  BTCUSDT 交易分析报告                          ║
╚════════════════════════════════════════════════════════════════╝

【市场趋势判断】
看多 - 资金费率正常，K线上升趋势，成交量温和放量

【关键位置】
支撑位: $42,000
阻力位: $45,000

【风险提示】
- 资金费率虽然正常，但需要关注是否突然上升
- 成交量虽然放量，但需要确认是否能持续

【交易建议】
开仓方向: 多
建议仓位: 中仓
止损位: $41,500
目标位: $45,500
信心度: 75%
```

## 配置API供应商

### 第三方供应商（推荐）

```env
LLM_API_BASE_URL=https://api.asxs.top
LLM_API_KEY=sk-your-key
MODEL_NAME=claude-sonnet-4-5-20250929
```

### 官方Anthropic API

```env
ANTHROPIC_API_KEY=sk-ant-your-key
MODEL_NAME=claude-3-5-sonnet-20241022
```

### AWS Bedrock

```env
LLM_API_BASE_URL=https://bedrock-runtime.us-east-1.amazonaws.com
LLM_API_KEY=your-aws-key
MODEL_NAME=anthropic.claude-3-5-sonnet-20241022-v2:0:200k
```

## 日志

日志文件保存在 `logs/trade_agent.log`

## 注意事项

⚠️ 本系统仅供学习和参考，不构成投资建议
⚠️ 加密货币交易风险极高，请谨慎决策
⚠️ 建议在模拟环境充分测试后再考虑实盘使用
⚠️ 爆仓数据和消息面数据需要配置相应的API密钥，否则将返回空数据
⚠️ 系统不使用模拟数据 - 无法获取真实数据时会在日志中说明并返回空值

## 许可证

MIT License
