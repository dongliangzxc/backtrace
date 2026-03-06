"""
全局配置文件
用于集中管理回测系统的各项配置参数
"""
import os

# ==================== 路径配置 ====================
# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据缓存目录
DATA_CACHE_DIR = os.path.join(BASE_DIR, "data", "cache")

# 回测报告输出目录
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# 确保目录存在
os.makedirs(DATA_CACHE_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ==================== 回测默认参数 ====================
# 初始资金（元）
DEFAULT_INITIAL_CASH = 100000.0

# 佣金费率（万分之三）
DEFAULT_COMMISSION_RATE = 0.0003

# 印花税率（千分之一，仅卖出时收取）
DEFAULT_STAMP_TAX_RATE = 0.001

# 过户费率（万分之0.2，双向收取）
DEFAULT_TRANSFER_FEE_RATE = 0.00002

# 最低佣金（元）
DEFAULT_MIN_COMMISSION = 5.0

# 最小交易单位（股，A股为100股/手）
DEFAULT_LOT_SIZE = 100

# ==================== 数据配置 ====================
# 数据缓存有效期（天），0表示永久有效
CACHE_EXPIRY_DAYS = 0

# 是否默认使用缓存
USE_CACHE_BY_DEFAULT = True

# akshare数据获取重试次数
AKSHARE_RETRY_COUNT = 3

# akshare请求间隔（秒）
AKSHARE_REQUEST_INTERVAL = 0.5

# ==================== 策略配置 ====================
# 双均线策略默认参数
MA_CROSS_SHORT_WINDOW = 5
MA_CROSS_LONG_WINDOW = 20

# MACD策略默认参数
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9

# RSI策略默认参数
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# ==================== 回测引擎配置 ====================
# 成交模式（可选值：NextOpen, NextClose, NextHighLowMid）
# NextHighLowMid: 下一根K线的(最高价+最低价)/2
EXECUTION_MODE = "NextHighLowMid"

# 是否允许卖空
ALLOW_SHORT = False

# ==================== 日志配置 ====================
# 日志级别（DEBUG, INFO, WARNING, ERROR）
LOG_LEVEL = "INFO"

# 是否打印详细日志
VERBOSE = True