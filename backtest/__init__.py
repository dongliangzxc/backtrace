"""
股票回测工具包
提供数据管理、策略开发、回测执行、结果分析等完整功能
"""

from backtest.data_manager import DataManager
from backtest.engine import BacktestEngine
from backtest.analyzer import Analyzer

__version__ = "1.0.0"

__all__ = [
    "DataManager",
    "BacktestEngine",
    "Analyzer",
]