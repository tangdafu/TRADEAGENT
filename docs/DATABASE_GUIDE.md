# 数据库功能说明

## 📊 当前状态

数据库功能目前处于**基础实现**阶段，主要用于数据持久化。

### ✅ 已实现功能

1. **自动保存分析结果**
   - 监控模式：自动保存所有分析
   
2. **数据存储**
   - 分析记录（时间、价格、信号、AI结果）
   - 价格记录（历史价格、成交量、资金费率）
   - 信号表现追踪（用于未来准确率统计）

3. **查询接口（已实现但未集成到CLI）**
   - `get_recent_analyses()` - 查询历史分析
   - `get_signal_statistics()` - 统计信号数据

---

## 🎯 设计目的

### 1. 数据积累
- 长期运行积累历史数据
- 为未来的策略优化提供数据基础
- 支持回测和准确率分析

### 2. 可选功能
- 不影响核心功能（实时分析和告警）
- 用户可以选择是否启用
- 灵活的扩展空间

### 3. 未来扩展
- 准确率统计
- 策略优化
- Web可视化
- 回测功能

---

## 💡 使用方式

### 启动监控（自动保存）

\`\`\`bash
# 监控模式自动保存所有分析结果
python src/main.py --symbols BTCUSDT --interval 15
\`\`\`

所有分析结果自动保存到 `data/trading_agent.db`

**注意：** v2.3.0 已移除单次分析功能，系统专注于持续监控。

---

## 🔍 手动查询数据

虽然CLI没有集成查询功能，但你可以通过Python脚本查询：

### 查询历史记录

\`\`\`python
from src.database import AnalysisRepository

repo = AnalysisRepository()

# 查询最近10条BTCUSDT的分析记录
records = repo.get_recent_analyses("BTCUSDT", limit=10)

for record in records:
    print(f"时间: {record['timestamp']}")
    print(f"价格: {record['current_price']}")
    print(f"趋势: {record['trend_direction']}")
    print(f"有交易机会: {record['has_trading_opportunity']}")
    print("-" * 50)
\`\`\`

### 统计信号数据

\`\`\`python
from src.database import AnalysisRepository

repo = AnalysisRepository()

# 统计最近7天的数据
stats = repo.get_signal_statistics("BTCUSDT", days=7)

print(f"总分析次数: {stats['total_analyses']}")
print(f"交易机会次数: {stats['opportunity_count']}")
print(f"机会率: {stats['opportunity_rate']:.2%}")
print(f"平均信心度: {stats['avg_confidence']:.2%}")
print(f"趋势分布: {stats['trend_distribution']}")
\`\`\`

### 使用SQLite工具查询

\`\`\`bash
# 使用sqlite3命令行工具
sqlite3 data/trading_agent.db

# 查询最近的分析记录
SELECT timestamp, symbol, current_price, trend_direction, has_trading_opportunity 
FROM analysis_records 
ORDER BY timestamp DESC 
LIMIT 10;

# 统计交易机会
SELECT 
    symbol,
    COUNT(*) as total,
    SUM(CASE WHEN has_trading_opportunity = 1 THEN 1 ELSE 0 END) as opportunities
FROM analysis_records
GROUP BY symbol;
\`\`\`

---

## 🚀 未来扩展方向

### 短期（可以快速实现）

1. **历史查询命令**
   \`\`\`bash
   python src/main.py --history BTCUSDT --days 7
   \`\`\`

2. **统计报告命令**
   \`\`\`bash
   python src/main.py --stats BTCUSDT --days 30
   \`\`\`

3. **准确率追踪**
   - 追踪信号后的价格变化
   - 计算信号准确率
   - 生成准确率报告

### 中期（需要一定开发）

1. **策略优化**
   - 基于历史数据优化阈值
   - A/B测试不同参数
   - 自动调整信号权重

2. **回测功能**
   - 模拟历史交易
   - 计算收益率
   - 风险评估

### 长期（需要较多开发）

1. **Web仪表板**
   - 可视化历史数据
   - 实时监控面板
   - 交互式图表

2. **机器学习优化**
   - 基于历史数据训练模型
   - 预测信号准确率
   - 自动优化策略

---

## 📝 数据库结构

### analysis_records（分析记录表）
- 分析时间、交易对、价格
- 是否有交易机会、触发的信号
- 趋势方向、信心度
- 支撑位、阻力位、止损位、目标位
- 完整的AI分析文本

### price_records（价格记录表）
- 历史价格数据
- 成交量
- 资金费率

### signal_performance（信号表现表）
- 信号触发时的价格
- 用于未来追踪准确率

---

## 💡 使用建议

### 如果你只需要实时信号
- 监控模式会自动保存所有分析
- 数据库文件会逐渐增大，定期清理即可

### 如果你想要数据分析
- 让监控模式长期运行，积累数据
- 定期使用Python脚本查询统计
- 等待未来的CLI查询功能

### 数据库维护
- 数据库文件位置：`data/trading_agent.db`
- 定期备份：`cp data/trading_agent.db data/backup/`
- 清理旧数据：删除数据库文件重新开始

---

## ❓ 常见问题

### Q: 数据库会影响性能吗？
A: 不会。SQLite写入非常快，对分析速度几乎无影响。

### Q: 数据库文件会很大吗？
A: 取决于运行时间。每条记录约1-2KB，运行一个月约几MB。

### Q: 可以禁用数据库吗？
A: 不可以。v2.3.0 开始，监控模式默认保存所有分析，这是核心功能。

### Q: 数据库损坏怎么办？
A: 删除 `data/trading_agent.db` 文件，系统会自动重新创建。

---

## 🎯 总结

**当前定位：**
- 数据库是一个**可选的辅助功能**
- 主要用于**数据积累**，为未来扩展做准备
- 不影响核心功能（实时分析和告警）

**使用建议：**
- 让它在后台默默积累数据
- 需要时可以手动查询
- 等待未来的功能扩展

**未来价值：**
- 策略优化的数据基础
- 准确率统计
- 回测和可视化

---

**更新时间**：2026-03-01  
**状态**：基础实现，可选功能




