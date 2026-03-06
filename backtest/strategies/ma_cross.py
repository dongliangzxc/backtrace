"""
双均线交叉策略
基于短期均线和长期均线的金叉死叉信号进行交易
"""
import numpy as np
import pandas as pd
from backtest.strategies.base_strategy import BaseStrategy
from config import MA_CROSS_SHORT_WINDOW, MA_CROSS_LONG_WINDOW


class MACrossStrategy(BaseStrategy):
    """
    双均线交叉策略
    
    信号逻辑：
    - 买入：短期均线上穿长期均线（金叉）
    - 卖出：短期均线下穿长期均线（死叉）
    """
    
    def __init__(
        self,
        short_window: int = MA_CROSS_SHORT_WINDOW,
        long_window: int = MA_CROSS_LONG_WINDOW
    ):
        """
        初始化双均线策略
        
        Args:
            short_window: 短期均线窗口（默认5）
            long_window: 长期均线窗口（默认20）
        """
        super().__init__(
            name="双均线策略",
            short_window=short_window,
            long_window=long_window
        )
        self.short_window = short_window
        self.long_window = long_window
        
        # 用于存储上一根K线的均线值，判断交叉
        self.prev_short_ma = None
        self.prev_long_ma = None
    
    def on_start(self):
        # 必须在on_start中设置历史数据深度，才能使用get_history
        self.set_history_depth(self.long_window + 2)
    
    def on_bar(self, bar):
        """
        每根K线的交易逻辑
        
        Args:
            bar: 当前K线数据
        """
        # get_history返回numpy数组，field默认为'close'
        close_arr = self.get_history(self.long_window + 1)
        
        # 如果历史数据不足，跳过
        if close_arr is None or len(close_arr) < self.long_window + 1:
            return
        
        # 将numpy数组转为Series以使用rolling
        close_series = pd.Series(close_arr)
        
        # 计算短期和长期均线
        short_ma = self.calculate_sma(close_series, self.short_window).iloc[-1]
        long_ma = self.calculate_sma(close_series, self.long_window).iloc[-1]
        
        # 获取当前持仓
        current_pos = self.get_position()
        
        # 如果有上一根K线的均线数据，判断交叉信号
        if self.prev_short_ma is not None and self.prev_long_ma is not None:
            
            # 金叉：短期均线上穿长期均线
            if (self.prev_short_ma <= self.prev_long_ma and 
                short_ma > long_ma and 
                current_pos == 0):
                # 全仓买入
                self.order_target_percent(target_percent=1.0)
            
            # 死叉：短期均线下穿长期均线
            elif (self.prev_short_ma >= self.prev_long_ma and 
                  short_ma < long_ma and 
                  current_pos > 0):
                # 全部卖出
                self.close_position()
        
        # 更新上一根K线的均线值
        self.prev_short_ma = short_ma
        self.prev_long_ma = long_ma
    
    def get_description(self) -> str:
        """
        获取策略描述
        
        Returns:
            策略描述字符串
        """
        return f"双均线策略(短期={self.short_window}, 长期={self.long_window})"