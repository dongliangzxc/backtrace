# 股票回测工具

一套基于 **akshare** 和 **akquant** 的完整股票回测系统，提供数据管理、策略开发、回测执行和结果分析等全流程功能。

## ✨ 功能特性

- 📦 **数据管理**: 自动缓存历史数据，支持增量更新，提升回测效率
- 🎯 **策略库**: 内置多个经典技术指标策略（双均线、MACD、RSI等）
- 🚀 **高性能**: 基于 akquant 的 Rust 核心引擎，回测速度快
- 📈 **专业分析**: 提供30+项回测指标，包含夏普比率、最大回撤等
- 📋 **可视化报告**: 自动生成交互式 HTML 报告，包含权益曲线、回撤图、收益分布等
- 🔧 **易扩展**: 模块化设计，轻松添加自定义策略

## 📦 安装

### 1. 克隆项目（如果还未克隆）

```bash
git clone <your-repo-url>
cd akshare
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

**核心依赖:**
- akshare >= 1.14.0
- akquant >= 0.1.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- pyarrow >= 14.0.0

## 🚀 快速开始

> **注意**: 本项目依赖 `akquant`（Rust 编译的回测引擎），需安装在指定 Python 环境中。
> 推荐使用 `run.sh` 启动脚本，自动使用正确的 Python 解释器，无需手动激活环境。

### 二哥战法单股回测

修改 `examples/eger_backtest.py` 顶部参数后运行：

```bash
# 修改 SYMBOL / GAP_UP_PCT / DROP_PCT 后执行
bash run.sh examples/eger_backtest.py
```

### 二哥战法批量扫描

修改 `examples/eger_scan.py` 中的 `SYMBOLS` 列表后运行：

```bash
bash run.sh examples/eger_scan.py
```

扫描结果分三档：
- ✅ **今日买入** — D1+D2 条件均已满足，今日开盘买入
- ⏳ **D1已触发，等D2** — 昨日出现高开低走形态，今日盯盘确认
- — **无信号** — 近期无形态

### 双均线策略回测示例

```bash
bash run.sh examples/simple_backtest.py
```

### 多策略对比

```bash
bash run.sh examples/compare_strategies.py
```

## 📚 项目结构

```
akshare/
├── backtest/                    # 回测核心模块
│   ├── __init__.py
│   ├── data_manager.py         # 数据管理（自动缓存+增量更新）
│   ├── engine.py               # 回测引擎
│   ├── analyzer.py             # 结果分析
│   └── strategies/             # 策略库
│       ├── __init__.py
│       ├── base_strategy.py    # 策略基类
│       ├── ma_cross.py         # 双均线策略
│       ├── macd_strategy.py    # MACD策略
│       ├── rsi_strategy.py     # RSI策略
│       └── eger_strategy.py    # 二哥战法策略
├── data/                        # 数据缓存目录
│   └── cache/                  # 本地 Parquet 缓存
├── reports/                     # 回测报告输出（HTML）
├── examples/                    # 使用示例
│   ├── simple_backtest.py      # 双均线策略回测
│   ├── compare_strategies.py   # 多策略对比
│   ├── eger_backtest.py        # 二哥战法单股回测
│   └── eger_scan.py            # 二哥战法批量扫描
├── config.py                    # 全局配置
├── run.sh                       # 启动脚本（推荐使用）
├── requirements.txt             # 依赖清单
└── README.md                    # 项目文档
```

## 🎯 内置策略

### 1. 二哥战法 (EgerStrategy)

**信号逻辑（4天循环）:**
- 第1天: 开盘较前日收盘涨幅 > 7%，且收盘较开盘跌幅 > 6%（高开低走）
- 第2天: 收盘 > 开盘（阳线），且收盘 < 第1天收盘
- 第3天: 开盘集合竞价**买入**
- 第4天: 开盘集合竞价**卖出**

**默认参数:** `gap_up_pct=7.0, drop_pct=6.0`

```python
from backtest.strategies import EgerStrategy

result = engine.run(
    symbol="688502",
    strategy_class=EgerStrategy,
    start_date="20200101",
    end_date="20260201",
    gap_up_pct=5.0,   # 自定义阈值
    drop_pct=4.0
)
```

### 2. 双均线策略 (MACrossStrategy)

**信号逻辑:**
- 买入: 短期均线上穿长期均线（金叉）
- 卖出: 短期均线下穿长期均线（死叉）

**默认参数:** `short_window=5, long_window=20`

```python
from backtest.strategies import MACrossStrategy

result = engine.run(
    symbol="300475",
    strategy_class=MACrossStrategy,
    start_date="20200101",
    end_date="20260201",
    short_window=10,  # 自定义参数
    long_window=30
)
```

### 2. MACD策略 (MACDStrategy)

**信号逻辑:**
- 买入: MACD柱状图由负转正（金叉）
- 卖出: MACD柱状图由正转负（死叉）

**默认参数:** `fast_period=12, slow_period=26, signal_period=9`

### 3. RSI策略 (RSIStrategy)

**信号逻辑:**
- 买入: RSI < 30（超卖）
- 卖出: RSI > 70（超买）

**默认参数:** `period=14, oversold=30, overbought=70`

## 🔧 自定义策略

继承 `BaseStrategy` 并实现 `on_bar` 方法：

```python
from backtest.strategies import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, param1=10, param2=20):
        super().__init__(
            name="我的策略",
            param1=param1,
            param2=param2
        )
        self.param1 = param1
        self.param2 = param2
    
    def on_bar(self, bar):
        # 获取历史数据
        history = self.get_history(bar.symbol, 50)
        if history is None or len(history) < 50:
            return
        
        # 实现你的交易逻辑
        current_pos = self.get_position(bar.symbol)
        
        # 买入条件
        if current_pos == 0 and <your_buy_condition>:
            self.order_target_percent(target_percent=1.0)
        
        # 卖出条件
        elif current_pos > 0 and <your_sell_condition>:
            self.close_position()
```

## 📊 回测指标说明

系统提供 30+ 项专业回测指标：

### 收益指标
- **总收益率**: 整个回测期间的收益率
- **年化收益率**: 折算为年化的收益率
- **最大回撤**: 历史最大资金回撤幅度

### 风险指标
- **夏普比率**: 衡量风险调整后收益，>1为可接受，>2为优秀
- **索提诺比率**: 只考虑下行风险的夏普比率
- **卡尔玛比率**: 年化收益率/最大回撤

### 交易指标
- **胜率**: 盈利交易占比
- **盈亏比**: 总盈利/总亏损
- **交易次数**: 完成的交易笔数

## ❓ 常见问题

### Q1: 数据缓存在哪里？如何清理？

**A:** 数据缓存在 `data/cache/` 目录，以 parquet 格式存储。

清理缓存：
```python
from backtest import DataManager

dm = DataManager()

# 清理指定股票
dm.clear_cache("300475")

# 清理所有缓存
dm.clear_cache()
```

### Q2: 如何更新缓存数据？

**A:** 使用 `update_cache` 方法：

```python
from backtest import DataManager

dm = DataManager()
dm.update_cache("300475")  # 增量更新
```

### Q3: 回测速度慢怎么办？

**A:** 优化建议：
1. 启用数据缓存（默认已启用）
2. 减少策略中的复杂计算
3. 使用向量化操作代替循环
4. 减少 `get_history` 的调用次数

### Q4: 回测结果与实盘差异大？

**A:** 可能原因：
1. **成交价格**: 回测使用模拟成交价，实盘存在滑点
2. **交易费用**: 确认配置的佣金/印花税与实际券商一致
3. **未来函数**: 检查策略是否使用了未来数据
4. **流动性**: 回测假设完全成交，实盘可能成交不足

建议：
- 在回测中设置更保守的交易成本
- 谨慎对待回测结果，建议模拟盘验证

### Q5: 如何添加更多技术指标？

**A:** 在 `BaseStrategy` 中已提供常用指标的计算方法：
- `calculate_sma()`: 简单移动平均
- `calculate_ema()`: 指数移动平均
- `calculate_rsi()`: RSI指标
- `calculate_macd()`: MACD指标
- `calculate_bollinger_bands()`: 布林带
- `calculate_atr()`: ATR波动率

也可以使用 pandas 或 ta-lib 等库计算其他指标。

### Q6: 支持分钟级数据吗？

**A:** 当前版本主要支持日线数据。分钟级数据需要：
1. 修改 `data_manager.py` 的数据获取接口
2. 确保 akshare 提供对应的分钟数据接口

### Q7: 如何设置止损止盈？

**A:** 在策略的 `on_bar` 方法中实现：

```python
def on_bar(self, bar):
    current_pos = self.get_position(bar.symbol)
    
    if current_pos > 0:
        # 获取持仓成本
        entry_price = self.get_avg_entry_price(bar.symbol)
        
        # 止损：亏损超过5%
        if bar.close < entry_price * 0.95:
            self.close_position()
        
        # 止盈：盈利超过10%
        elif bar.close > entry_price * 1.10:
            self.close_position()
```

## 🛠️ 配置说明

在 `config.py` 中可以修改全局配置：

```python
# 回测默认参数
DEFAULT_INITIAL_CASH = 100000.0       # 初始资金
DEFAULT_COMMISSION_RATE = 0.0003      # 佣金费率（万三）
DEFAULT_STAMP_TAX_RATE = 0.001        # 印花税率（千一）
DEFAULT_LOT_SIZE = 100                # 最小交易单位

# 策略默认参数
MA_CROSS_SHORT_WINDOW = 5             # 双均线短期窗口
MA_CROSS_LONG_WINDOW = 20             # 双均线长期窗口
RSI_PERIOD = 14                       # RSI周期
```

## 📄 许可证

本项目仅供学习和研究使用，不构成任何投资建议。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

如有问题或建议，欢迎通过 Issue 反馈。

---

**⚠️ 风险提示**: 回测结果不代表未来表现，量化投资存在风险，请谨慎决策。