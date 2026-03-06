"""
策略库模块
包含各种技术指标策略的实现
"""

from backtest.strategies.base_strategy import BaseStrategy
from backtest.strategies.ma_cross import MACrossStrategy
from backtest.strategies.macd_strategy import MACDStrategy
from backtest.strategies.rsi_strategy import RSIStrategy
from backtest.strategies.eger_strategy import EgerStrategy

__all__ = [
    "BaseStrategy",
    "MACrossStrategy",
    "MACDStrategy",
    "RSIStrategy",
    "EgerStrategy",
]