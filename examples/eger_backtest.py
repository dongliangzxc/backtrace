"""
二哥战法回测示例
修改下方配置参数，即可对任意股票运行回测
"""
from backtest import BacktestEngine, Analyzer
from backtest.strategies import EgerStrategy

# ===== 在这里修改参数 =====
SYMBOL     = "300570"    # 股票代码
START_DATE = "20250101"  # 开始日期
END_DATE   = "20260301"  # 结束日期
GAP_UP_PCT = 7.0         # 第1天：开盘较前日收盘涨幅阈值（%）
DROP_PCT   = 6.0         # 第1天：收盘较开盘跌幅阈值（%）
INITIAL_CASH = 100000.0  # 初始资金
# ==========================


def main():
    print("=" * 60)
    print(f"二哥战法回测  股票:{SYMBOL}  {START_DATE}~{END_DATE}")
    print(f"条件: 开盘涨幅>{GAP_UP_PCT}%  日内跌幅>{DROP_PCT}%")
    print("=" * 60)

    engine = BacktestEngine(initial_cash=INITIAL_CASH)
    result = engine.run(
        symbol=SYMBOL,
        strategy_class=EgerStrategy,
        start_date=START_DATE,
        end_date=END_DATE,
        gap_up_pct=GAP_UP_PCT,
        drop_pct=DROP_PCT,
    )

    analyzer = Analyzer()
    analyzer.print_summary(result, strategy_name=f"二哥战法({GAP_UP_PCT}%/{DROP_PCT}%)")

    # 交易明细
    trades = result.trades
    print(f"\n交易明细（共 {len(trades)} 笔）:")
    if trades:
        print(f"{'序号':>3}  {'买入日':^12}  {'开盘买@':>8}  {'卖出日':^12}  {'开盘卖@':>8}  {'盈亏(元)':>10}  {'收益率':>8}")
        print("-" * 72)
        import pandas as pd
        for i, t in enumerate(trades):
            entry_d = pd.Timestamp(t.entry_time).date() if not hasattr(t.entry_time, 'date') else t.entry_time.date()
            exit_d  = pd.Timestamp(t.exit_time).date()  if not hasattr(t.exit_time,  'date') else t.exit_time.date()
            print(f"{i+1:>3}  {str(entry_d):^12}  {t.entry_price:>8.2f}"
                  f"  {str(exit_d):^12}  {t.exit_price:>8.2f}"
                  f"  {t.pnl:>10.0f}  {t.return_pct:>7.2f}%")
    else:
        print("  该股在此区间内未出现符合二哥战法形态的信号")

    # 生成 HTML 报告
    report_path = analyzer.save_report(
        result,
        filename=f"eger_{SYMBOL}_report.html",
        show=True
    )
    print(f"\n✅ 报告已保存: {report_path}")
    return result


if __name__ == "__main__":
    main()