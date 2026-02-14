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

# 详细输出
python src/main.py --verbose
```

## 功能特性

- 🔄 **实时数据采集** - 从币安API获取市场数据
- 📊 **多维度分析** - 资金费率、K线成交量、爆仓数据
- 🤖 **AI智能分析** - 使用Claude进行深度分析
- 💡 **交易建议** - 给出具体的交易方向和风险提示

## 核心因素

1. **资金费率** - 反映多空拥挤度
2. **K线与成交量** - 技术面分析
3. **爆仓数据** - 市场情绪指标

## 项目结构

```
src/
├── main.py                    # 主程序入口
├── data_collectors/           # 数据采集模块
│   ├── base.py
│   ├── funding_rate.py
│   ├── kline_volume.py
│   └── liquidation.py
├── analyzers/                 # 数据分析模块
│   └── factor_analyzer.py
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

## 许可证

MIT License
