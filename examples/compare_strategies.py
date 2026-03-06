"""
多策略对比示例
演示如何对比多个策略的回测效果
"""
from backtest import BacktestEngine, Analyzer
from backtest.strategies import MACrossStrategy, MACDStrategy, RSIStrategy

# 配置参数
SYMBOL = "300475"  # 股票代码：立讯精密
START_DATE = "20200101"  # 开始日期
END_DATE = "20260201"  # 结束日期
INITIAL_CASH = 100000.0  # 初始资金：10万元


def main():
    """
    主函数：对比多个策略的回测效果
    """
    print("="*60)
    print("股票回测工具 - 多策略对比示例")
    print("="*60)
    
    # 1. 创建回测引擎
    print("\n【步骤1】初始化回测引擎...")
    engine = BacktestEngine(initial_cash=INITIAL_CASH)
    
    # 2. 定义要对比的策略
    print("\n【步骤2】定义对比策略...")
    strategies = [
        {
            "strategy_class": MACrossStrategy,
            "params": {"short_window": 5, "long_window": 20},
            "name": "双均线(5/20)"
        },
        {
            "strategy_class": MACrossStrategy,
            "params": {"short_window": 10, "long_window": 30},
            "name": "双均线(10/30)"
        },
        {
            "strategy_class": MACDStrategy,
            "params": {},  # 使用默认参数
            "name": "MACD策略"
        },
        {
            "strategy_class": RSIStrategy,
            "params": {"period": 14, "oversold": 30, "overbought": 70},
            "name": "RSI策略"
        }
    ]
    
    print(f"将对比 {len(strategies)} 个策略:")
    for idx, s in enumerate(strategies, 1):
        print(f"  {idx}. {s['name']}")
    
    # 3. 运行对比回测
    print(f"\n【步骤3】运行对比回测...")
    print(f"股票代码: {SYMBOL}")
    print(f"回测区间: {START_DATE} ~ {END_DATE}")
    print("正在执行回测，请稍候...\n")
    
    comparison_df = engine.compare_strategies(
        symbol=SYMBOL,
        strategies=strategies,
        start_date=START_DATE,
        end_date=END_DATE
    )
    
    # 4. 展示对比结果
    print("\n【步骤4】展示对比结果...")
    analyzer = Analyzer()
    analyzer.print_comparison(comparison_df)
    
    # 5. 保存对比结果
    print("【步骤5】保存对比结果...")
    csv_path = analyzer.save_comparison(
        comparison_df,
        filename="strategy_comparison.csv"
    )
    print(f"对比结果已保存到: {csv_path}")
    
    # 6. 分别生成各策略的详细报告（可选）
    print("\n【步骤6】生成各策略的详细报告...")
    results = {}
    
    for idx, strategy_config in enumerate(strategies, 1):
        print(f"正在生成策略 {idx}/{len(strategies)} 的报告...")
        
        result = engine.run(
            symbol=SYMBOL,
            strategy_class=strategy_config["strategy_class"],
            start_date=START_DATE,
            end_date=END_DATE,
            **strategy_config["params"]
        )
        
        # 保存报告
        report_filename = f"strategy_{idx}_{strategy_config['name'].replace('/', '_')}.html"
        analyzer.save_report(
            result,
            filename=report_filename,
            show=False  # 不自动打开，避免打开太多窗口
        )
        
        results[strategy_config["name"]] = result
    
    print(f"\n✅ 对比完成！所有报告已保存到 reports/ 目录")
    print("\n" + "="*60)
    
    # 7. 简要分析（可选）
    print("\n【分析建议】")
    
    # 找出收益率最高的策略
    best_return_idx = comparison_df["总收益率(%)"].idxmax()
    print(f"📈 收益率最高: {best_return_idx} ({comparison_df.loc[best_return_idx, '总收益率(%)']:.2f}%)")
    
    # 找出夏普比率最高的策略
    best_sharpe_idx = comparison_df["夏普比率"].idxmax()
    print(f"⚖️  夏普比率最高: {best_sharpe_idx} ({comparison_df.loc[best_sharpe_idx, '夏普比率']:.2f})")
    
    # 找出最大回撤最小的策略
    best_drawdown_idx = comparison_df["最大回撤(%)"].idxmin()
    print(f"🛡️  最大回撤最小: {best_drawdown_idx} ({comparison_df.loc[best_drawdown_idx, '最大回撤(%)']:.2f}%)")
    
    # 找出胜率最高的策略
    best_winrate_idx = comparison_df["胜率(%)"].idxmax()
    print(f"🎯 胜率最高: {best_winrate_idx} ({comparison_df.loc[best_winrate_idx, '胜率(%)']:.2f}%)")
    
    print("\n💡 提示: 请结合多个指标综合评估策略表现，不要只看单一指标。")
    print("   建议优先关注夏普比率、卡尔玛比率等风险调整后收益指标。")
    
    return comparison_df, results


if __name__ == "__main__":
    comparison_df, results = main()