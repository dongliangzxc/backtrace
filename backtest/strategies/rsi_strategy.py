"""
RSI策略
基于RSI指标的超买超卖信号进行交易
"""
import pandas as pd
from backtest.strategies.base_strategy import BaseStrategy
from config import RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT


class RSIStrategy(BaseStrategy):
    """
    RSI策略
    
    信号逻辑：
    - 买入：RSI < 超卖阈值（默认30）
    - 卖出：RSI > 超买阈值（默认70）
    """
    
    def __init__(
        self,
        period: int = RSI_PERIOD,
        oversold: float = RSI_OVERSOLD,
        overbought: float = RSI_OVERBOUGHT
    ):
        """
        初始化RSI策略
        
        Args:
            period: RSI计算周期（默认14）
            oversold: 超卖阈值（默认30）
            overbought: 超买阈值（默认70）
        """
        super().__init__(
            name="RSI策略",
            period=period,
            oversold=oversold,
            overbought=overbought
        )
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def on_start(self):
        # 必须在on_start中设置历史数据深度，才能使用get_history
        self.set_history_depth(self.period + 11)
    
    def on_bar(self, bar):
        """
        每根K线的交易逻辑
        
        Args:
            bar: 当前K线数据
        """
        # 获取历史数据（需要足够的数据计算RSI）
        lookback = self.period + 10
        # get_history返回numpy数组，field默认为'close'
        close_arr = self.get_history(lookback)
        
        # 如果历史数据不足，跳过
        if close_arr is None or len(close_arr) < lookback:
            return
        
        # 将numpy数组转为Series以计算指标
        close_series = pd.Series(close_arr)
        
        # 计算RSI指标
        rsi = self.calculate_rsi(close_series, self.period)
        
        # 获取当前RSI值
        current_rsi = rsi.iloc[-1]
        
        # 如果数据无效，跳过
        if pd.isna(current_rsi):
            return
        
        # 获取当前持仓
        current_pos = self.get_position()
        
        # 超卖信号：RSI < 超卖阈值，买入
        if current_rsi < self.oversold and current_pos == 0:
            # 全仓买入
            self.order_target_percent(target_percent=1.0)
        
        # 超买信号：RSI > 超买阈值，卖出
        elif current_rsi > self.overbought and current_pos > 0:
            # 全部卖出
            self.close_position()
    
    def get_description(self) -> str:
        """
        获取策略描述
        
        Returns:
            策略描述字符串
        """
        return (f"RSI策略(周期={self.period}, "
                f"超卖={self.oversold}, "
                f"超买={self.overbought})")