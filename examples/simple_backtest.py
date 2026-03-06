"""
简单回测示例
演示如何使用回测工具进行单个策略的完整回测
"""
from backtest import BacktestEngine, Analyzer
from backtest.strategies import MACrossStrategy

# 配置参数
SYMBOL = "300475"  # 股票代码：立讯精密
START_DATE = "20200101"  # 开始日期
END_DATE = "20260201"  # 结束日期
INITIAL_CASH = 100000.0  # 初始资金：10万元

def main():
    """
    主函数：演示完整的回测流程
    """
    print("="*60)
    print("股票回测工具 - 简单回测示例")
    print("="*60)
    
    # 1. 创建回测引擎
    print("\n【步骤1】初始化回测引擎...")
    engine = BacktestEngine(initial_cash=INITIAL_CASH)
    
    # 2. 运行回测
    print(f"\n【步骤2】运行回测...")
    print(f"股票代码: {SYMBOL}")
    print(f"回测区间: {START_DATE} ~ {END_DATE}")
    print(f"使用策略: 双均线策略(短期=5, 长期=20)")
    
    result = engine.run(
        symbol=SYMBOL,
        strategy_class=MACrossStrategy,
        start_date=START_DATE,
        end_date=END_DATE,
        # 策略参数（可选，这里使用默认值）
        short_window=5,
        long_window=20
    )
    
    # 3. 分析结果
    print("\n【步骤3】分析回测结果...")
    analyzer = Analyzer()
    
    # 打印核心指标摘要
    analyzer.print_summary(result, strategy_name="双均线策略(5/20)")
    
    # 4. 生成可视化报告
    print("【步骤4】生成可视化报告...")
    report_path = analyzer.save_report(
        result,
        filename="simple_backtest_report.html",
        show=True  # 自动在浏览器中打开
    )
    
    print(f"\n✅ 回测完成！报告已保存到: {report_path}")
    print("\n" + "="*60)
    
    # 5. 查看详细交易记录（可选）
    print("\n【可选】查看交易明细...")
    trades_df = result.trades_df
    if not trades_df.empty:
        print(f"\n交易明细（共 {len(trades_df)} 笔）:")
        print(trades_df[['entry_time', 'exit_time', 'entry_price', 'exit_price', 'pnl', 'return_pct']].head(10))
        print("\n...")
        print(f"（仅显示前10笔，完整记录请查看HTML报告）")
    
    return result


if __name__ == "__main__":
    result = main()