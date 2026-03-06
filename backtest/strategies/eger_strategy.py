"""
二哥战法策略
特定K线形态识别后的短线交易策略
"""
import numpy as np
from backtest.strategies.base_strategy import BaseStrategy


class EgerStrategy(BaseStrategy):
    """
    二哥战法策略

    形态识别逻辑（4天循环）：
    - 第1天（信号日）：开盘涨幅超过9%，且收盘较开盘下跌超过8%
    - 第2天（确认日）：收盘价 > 开盘价（阳线），且收盘价 < 第1天收盘价
    - 第3天：开盘集合竞价买入（市价单开盘买入）
    - 第4天：开盘集合竞价卖出（市价单开盘卖出）
    """

    def __init__(
        self,
        gap_up_pct: float = 5.0,
        drop_pct: float = 4.0,
    ):
        """
        初始化二哥战法策略

        Args:
            gap_up_pct: 第1天开盘较前日收盘涨幅阈值（%），默认5%
            drop_pct: 第1天收盘较开盘下跌幅度阈值（%），默认4%

        注意：该形态在A股出现频率较低（通常只在板块活跃的强势股中出现）。
        """
        super().__init__(
            name="二哥战法",
            gap_up_pct=gap_up_pct,
            drop_pct=drop_pct,
        )
        self.gap_up_pct = gap_up_pct
        self.drop_pct = drop_pct

        # 状态机：None / 'day1_confirmed' / 'wait_buy' / 'wait_sell'
        self._state = None
        self._day1_close = None   # 第1天收盘价，供第2天判断用

    def on_start(self):
        # 需要 2 根历史K线：获取前日收盘（field='close'）用于计算开盘涨幅
        self.set_history_depth(3)

    def on_bar(self, bar):
        open_price  = bar.open
        close_price = bar.close

        # ── 状态机 ──────────────────────────────────────────────
        # 状态: wait_sell → 今日开盘卖出（第4天）
        if self._state == 'wait_sell':
            if self.get_position() > 0:
                self.close_position()
            self._state = None
            self._day1_close = None
            return

        # 状态: wait_buy → 今日开盘买入（第3天），下一根K线等待卖出
        if self._state == 'wait_buy':
            if self.get_position() == 0:
                self.order_target_percent(target_percent=1.0)
            self._state = 'wait_sell'
            return

        # 状态: day1_confirmed → 判断第2天确认条件
        if self._state == 'day1_confirmed':
            # 第2天条件：阳线（收盘 > 开盘）且收盘低于第1天收盘
            if close_price > open_price and close_price < self._day1_close:
                self._state = 'wait_buy'   # 明天开盘买入
            else:
                # 条件不满足，重置状态继续扫描
                self._state = None
                self._day1_close = None
            return

        # 默认状态: 扫描第1天信号
        # get_history(2,'close') 返回 [前日收盘, 当日收盘]
        close_arr = self.get_history(2, field='close')
        if close_arr is None or len(close_arr) < 2:
            return
        prev_close = close_arr[-2]   # 前日收盘（用于计算开盘涨幅）
        if prev_close <= 0:
            return

        # 第1天条件1：开盘较前日收盘涨幅 > gap_up_pct%
        open_gap_pct = (open_price - prev_close) / prev_close * 100
        if open_gap_pct <= self.gap_up_pct:
            return

        # 第1天条件2：收盘较开盘跌幅 > drop_pct%（高开低走形态）
        intraday_drop_pct = (open_price - close_price) / open_price * 100
        if intraday_drop_pct <= self.drop_pct:
            return

        # 第1天信号成立
        self._state = 'day1_confirmed'
        self._day1_close = close_price

    def get_description(self) -> str:
        return f"二哥战法(开盘涨幅>{self.gap_up_pct}%, 日内跌幅>{self.drop_pct}%)"