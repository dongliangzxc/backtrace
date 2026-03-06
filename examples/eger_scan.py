"""
二哥战法批量扫描器
检测给定股票列表中，今日是否满足"开盘买入"条件（即昨日为第2天确认日）

用法：直接修改下方 SYMBOLS 列表，然后运行：
    bash run.sh examples/eger_scan.py
"""
import sys
import os
import datetime
import pandas as pd

# 确保项目根目录在路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backtest.data_manager import DataManager

# ===== 在这里填入要扫描的股票代码 =====
SYMBOLS = [
    # 半导体/芯片
    "603501", "688981", "688012", "688041", "688099",
    "688169", "688008", "688036", "688116", "688049",
    "688072", "688368", "688425", "688521", "688023",
    "688382", "688111", "688223", "688256", "688390",
    # AI/算力/数字经济
    "300259", "002230", "300496", "688271", "300308",
    "300474", "002415", "300168", "300033", "002161",
    "300188", "688789", "688777", "300418", "300667",
    "300454", "300212", "002410", "300666", "688393",
    # 新能源/储能/锂电
    "300750", "002594", "300014", "002460", "603659",
    "300763", "688567", "300896", "301230", "300618",
    "002129", "300316", "002506", "300285", "301358",
    "688690", "301155", "300274", "002920", "300604",
    # 医药/创新药/CXO
    "300759", "603259", "688180", "688321", "300122",
    "002007", "300015", "300661", "300146", "688185",
    "688388", "300347", "300529", "688508", "300760",
    "688363", "301269", "688589", "688321",
    # 军工/航天
    "600760", "002414", "300162", "300541", "688178",
    "002025", "600467", "300827", "300217", "600316",
    # 机器人/自动化
    "688296", "300690", "300433", "002747", "300396",
    "301510", "300769", "300970", "688169", "300480",
    # 消费电子/苹果链
    "002475", "002241", "300115", "300782", "002049",
    "300773", "002384", "300876", "688106", "300244",
    # 光伏/风电
    "601012", "300450", "002531", "688599", "300770",
    "002714", "301236", "688330", "300896", "300979",
    # 汽车智能化/零部件
    "603127", "301005", "300442", "002463", "600601",
    "300776", "301045", "601865", "301526", "300570",
    # 创业板高弹性
    "300475", "300478", "300832", "300866", "300919",
    "300957", "301020", "301038", "301069", "301088",
    "301106", "301136", "301163", "301175", "301196",
    "301208", "301226", "300667", "300454", "300212",
    # 科创板高弹性
    "688001", "688002", "688003", "688006", "688007",
    "688009", "688010", "688011", "688015", "688016",
    "688017", "688018", "688019", "688020", "688021",
    "688025", "688026", "688027", "688028", "688029",
]
# ===== 第1天形态阈值 =====
GAP_UP_PCT = 7.0   # 开盘较前收涨幅 >7%
DROP_PCT   = 6.0   # 收盘较开盘跌幅 >6%
# ==================================

DAYS_TO_FETCH = 10   # 用于判断形态的最近交易日数
# 扫描时拉取最近180天，兼顾增量更新与缓存命中
SCAN_START = (datetime.date.today() - datetime.timedelta(days=180)).strftime("%Y%m%d")
SCAN_END   = datetime.date.today().strftime("%Y%m%d")

_dm = DataManager()


def fetch_recent(symbol: str) -> pd.DataFrame | None:
    """通过 DataManager 获取数据（自动缓存+增量更新），直接读缓存避免重复拉取"""
    try:
        cache_path = _dm._get_cache_path(symbol)
        if os.path.exists(cache_path):
            # 已有缓存：增量更新后直接读 parquet，不走 get_stock_data 的日期范围判断
            _dm.update_cache(symbol)
            df = pd.read_parquet(cache_path)
        else:
            # 首次：通过 get_stock_data 拉取并缓存
            df = _dm.get_stock_data(symbol, SCAN_START, SCAN_END, use_cache=True)

        if df is None or df.empty:
            return None
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values("date").tail(DAYS_TO_FETCH).reset_index(drop=True)
        return df
    except Exception as e:
        print(f"  [{symbol}] 获取数据失败: {e}")
        return None


def check_signal(symbol: str, df: pd.DataFrame) -> dict:
    """
    检查最新两根K线是否满足二哥战法买入条件：
    - 倒数第2根（昨日）= Day2确认：阳线 且 收盘 < Day1收盘
    - 倒数第3根（前日）= Day1信号：开盘涨幅>GAP_UP_PCT 且 日内跌幅>DROP_PCT
    返回信号状态字典
    """
    if len(df) < 3:
        return {"symbol": symbol, "signal": "数据不足", "detail": ""}

    d1  = df.iloc[-3]   # Day1候选
    d2  = df.iloc[-2]   # Day2确认候选
    # 今日为Day3，应开盘买入

    prev = df.iloc[-4] if len(df) >= 4 else None
    if prev is None:
        return {"symbol": symbol, "signal": "数据不足", "detail": ""}

    # Day1条件
    open_gap = (d1["open"] - prev["close"]) / prev["close"] * 100
    intraday_drop = (d1["open"] - d1["close"]) / d1["open"] * 100
    day1_ok = open_gap > GAP_UP_PCT and intraday_drop > DROP_PCT

    # Day2条件
    yang = d2["close"] > d2["open"]
    below_d1 = d2["close"] < d1["close"]
    day2_ok = yang and below_d1

    today = df.iloc[-1]["date"].date()
    d1_date = d1["date"].date()
    d2_date = d2["date"].date()

    detail = (
        f"D1:{d1_date} 开盘涨{open_gap:.1f}% 日内跌{intraday_drop:.1f}%  "
        f"D2:{d2_date} 阳线={yang} 低于D1={below_d1}"
    )

    if day1_ok and day2_ok:
        return {"symbol": symbol, "signal": "✅ 今日买入", "detail": detail}
    elif day1_ok and not day2_ok:
        return {"symbol": symbol, "signal": "⏳ D1已触发,等D2", "detail": detail}
    else:
        return {"symbol": symbol, "signal": "—  无信号", "detail": ""}


def main():
    today = datetime.date.today()
    print("=" * 65)
    print(f"二哥战法批量扫描  {today}  阈值: 开盘涨>{GAP_UP_PCT}% 日内跌>{DROP_PCT}%")
    print("=" * 65)

    buy_list   = []
    watch_list = []
    no_signal  = []

    for symbol in SYMBOLS:
        sys.stdout.write(f"  扫描 {symbol} ...")
        sys.stdout.flush()
        df = fetch_recent(symbol)
        if df is None:
            no_signal.append({"symbol": symbol, "signal": "获取失败", "detail": ""})
            print(" 失败")
            continue
        result = check_signal(symbol, df)
        print(f" {result['signal']}")
        if "买入" in result["signal"]:
            buy_list.append(result)
        elif "等D2" in result["signal"]:
            watch_list.append(result)
        else:
            no_signal.append(result)

    print("\n" + "=" * 65)
    print(f"【今日买入信号】共 {len(buy_list)} 只")
    for r in buy_list:
        print(f"  {r['symbol']}  {r['detail']}")

    print(f"\n【关注中（D1已触发）】共 {len(watch_list)} 只")
    for r in watch_list:
        print(f"  {r['symbol']}  {r['detail']}")

    if not buy_list and not watch_list:
        print("\n  今日无任何符合条件的股票")
    print("=" * 65)


if __name__ == "__main__":
    main()