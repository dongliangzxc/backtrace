"""
MACD策略
基于MACD指标的金叉死叉信号进行交易
"""
import pandas as pd
from backtest.strategies.base_strategy import BaseStrategy
from config import MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD


class MACDStrategy(BaseStrategy):
    """
    MACD策略
    
    信号逻辑：
    - 买入：MACD柱状图由负转正（金叉）
    - 卖出：MACD柱状图由正转负（死叉）
    """
    
    def __init__(
        self,
        fast_period: int = MACD_FAST_PERIOD,
        slow_period: int = MACD_SLOW_PERIOD,
        signal_period: int = MACD_SIGNAL_PERIOD
    ):
        """
        初始化MACD策略
        
        Args:
            fast_period: 快线周期（默认12）
            slow_period: 慢线周期（默认26）
            signal_period: 信号线周期（默认9）
        """
        super().__init__(
            name="MACD策略",
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period
        )
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        
        # 用于存储上一根K线的MACD柱状图值
        self.prev_histogram = None
    
    def on_start(self):
        # 必须在on_start中设置历史数据深度，才能使用get_history
        lookback = self.slow_period + self.signal_period + 10
        self.set_history_depth(lookback + 1)
    
    def on_bar(self, bar):
        """
        每根K线的交易逻辑
        
        Args:
            bar: 当前K线数据
        """
        # 获取历史数据（需要足够的数据计算MACD）
        lookback = self.slow_period + self.signal_period + 10
        # get_history返回numpy数组，field默认为'close'
        close_arr = self.get_history(lookback)
        
        # 如果历史数据不足，跳过
        if close_arr is None or len(close_arr) < lookback:
            return
        
        # 将numpy数组转为Series以计算指标
        close_series = pd.Series(close_arr)
        
        # 计算MACD指标
        macd_line, signal_line, histogram = self.calculate_macd(
            close_series,
            self.fast_period,
            self.slow_period,
            self.signal_period
        )
        
        # 获取当前柱状图值
        current_histogram = histogram.iloc[-1]
        
        # 如果数据无效，跳过
        if pd.isna(current_histogram):
            return
        
        # 获取当前持仓
        current_pos = self.get_position()
        
        # 如果有上一根K线的柱状图值，判断交叉信号
        if self.prev_histogram is not None:
            
            # 金叉：柱状图由负转正
            if self.prev_histogram <= 0 and current_histogram > 0 and current_pos == 0:
                # 全仓买入
                self.order_target_percent(target_percent=1.0)
            
            # 死叉：柱状图由正转负
            elif self.prev_histogram >= 0 and current_histogram < 0 and current_pos > 0:
                # 全部卖出
                self.close_position()
        
        # 更新上一根K线的柱状图值
        self.prev_histogram = current_histogram
    
    def get_description(self) -> str:
        """
        获取策略描述
        
        Returns:
            策略描述字符串
        """
        return (f"MACD策略(快线={self.fast_period}, "
                f"慢线={self.slow_period}, "
                f"信号线={self.signal_period})")