"""
策略基类
定义策略接口规范和常用技术指标计算方法
"""
import numpy as np
import pandas as pd
from akquant import Strategy


class BaseStrategy(Strategy):
    """
    策略基类
    所有自定义策略都应继承此类并实现 on_bar 方法
    
    注意：akquant.Strategy.__init__ 不接受任何参数，
    因此策略参数需在子类 __init__ 中通过实例属性设置。
    """
    
    def __init__(self, name: str = "BaseStrategy", **params):
        """
        初始化策略
        
        Args:
            name: 策略名称
            **params: 策略参数
        """
        super().__init__()
        self._strategy_name = name
        self._strategy_params = params
    
    def on_bar(self, bar):
        """
        每根K线触发的回调函数（子类必须重写此方法）
        
        Args:
            bar: 当前K线数据对象
        """
        raise NotImplementedError("子类必须实现 on_bar 方法")
    
    def get_description(self) -> str:
        """
        获取策略描述信息
        
        Returns:
            策略描述字符串
        """
        param_str = ", ".join([f"{k}={v}" for k, v in self._strategy_params.items()])
        return f"{self._strategy_name}({param_str})"
    
    # ==================== 技术指标计算辅助方法 ====================
    
    @staticmethod
    def calculate_sma(data: pd.Series, window: int) -> pd.Series:
        """
        计算简单移动平均线（SMA）
        
        Args:
            data: 价格序列
            window: 窗口大小
            
        Returns:
            SMA序列
        """
        return data.rolling(window=window).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, span: int) -> pd.Series:
        """
        计算指数移动平均线（EMA）
        
        Args:
            data: 价格序列
            span: 时间跨度
            
        Returns:
            EMA序列
        """
        return data.ewm(span=span, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        计算相对强弱指标（RSI）
        
        Args:
            data: 价格序列
            period: 周期
            
        Returns:
            RSI序列
        """
        # 计算价格变化
        delta = data.diff()
        
        # 分离涨跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 计算平均涨跌幅
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # 计算RS和RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> tuple:
        """
        计算MACD指标
        
        Args:
            data: 价格序列
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            (macd_line, signal_line, histogram) 元组
        """
        # 计算快线和慢线
        ema_fast = BaseStrategy.calculate_ema(data, fast_period)
        ema_slow = BaseStrategy.calculate_ema(data, slow_period)
        
        # MACD线 = 快线 - 慢线
        macd_line = ema_fast - ema_slow
        
        # 信号线 = MACD的EMA
        signal_line = BaseStrategy.calculate_ema(macd_line, signal_period)
        
        # 柱状图 = MACD - 信号线
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(
        data: pd.Series,
        window: int = 20,
        num_std: float = 2.0
    ) -> tuple:
        """
        计算布林带
        
        Args:
            data: 价格序列
            window: 窗口大小
            num_std: 标准差倍数
            
        Returns:
            (upper_band, middle_band, lower_band) 元组
        """
        middle_band = BaseStrategy.calculate_sma(data, window)
        std = data.rolling(window=window).std()
        
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        计算平均真实波幅（ATR）
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期
            
        Returns:
            ATR序列
        """
        # 真实波幅 = max(H-L, |H-C_prev|, |L-C_prev|)
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr