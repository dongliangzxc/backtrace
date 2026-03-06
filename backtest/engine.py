"""
回测引擎
封装akquant的run_backtest，提供更友好的接口
"""
import logging
from typing import Type, Dict, List, Optional
import pandas as pd
import akquant as aq
from backtest.data_manager import DataManager
from backtest.strategies.base_strategy import BaseStrategy
from config import (
    DEFAULT_INITIAL_CASH,
    DEFAULT_COMMISSION_RATE,
    DEFAULT_STAMP_TAX_RATE,
    DEFAULT_TRANSFER_FEE_RATE,
    DEFAULT_MIN_COMMISSION,
    DEFAULT_LOT_SIZE,
    EXECUTION_MODE,
    LOG_LEVEL,
    VERBOSE
)

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    回测引擎
    提供简洁的回测接口和多策略对比功能
    """
    
    def __init__(
        self,
        initial_cash: float = DEFAULT_INITIAL_CASH,
        commission_rate: float = DEFAULT_COMMISSION_RATE,
        stamp_tax_rate: float = DEFAULT_STAMP_TAX_RATE,
        transfer_fee_rate: float = DEFAULT_TRANSFER_FEE_RATE,
        min_commission: float = DEFAULT_MIN_COMMISSION,
        lot_size: int = DEFAULT_LOT_SIZE
    ):
        """
        初始化回测引擎
        
        Args:
            initial_cash: 初始资金（元）
            commission_rate: 佣金费率
            stamp_tax_rate: 印花税率（仅卖出）
            transfer_fee_rate: 过户费率
            min_commission: 最低佣金（元）
            lot_size: 最小交易单位（股）
        """
        self.initial_cash = initial_cash
        self.commission_rate = commission_rate
        self.stamp_tax_rate = stamp_tax_rate
        self.transfer_fee_rate = transfer_fee_rate
        self.min_commission = min_commission
        self.lot_size = lot_size
        
        # 初始化数据管理器
        self.data_manager = DataManager()
        
        # 解析执行模式
        self.execution_mode = self._parse_execution_mode(EXECUTION_MODE)
        
        if VERBOSE:
            logger.info("回测引擎初始化完成")
            logger.info(f"初始资金: {self.initial_cash:,.0f} 元")
            logger.info(f"佣金费率: {self.commission_rate*10000:.1f} 万分之")
            logger.info(f"印花税率: {self.stamp_tax_rate*1000:.1f} 千分之")
    
    def _parse_execution_mode(self, mode_str: str):
        """
        解析执行模式字符串
        
        Args:
            mode_str: 模式字符串
            
        Returns:
            akquant的ExecutionMode对象
        """
        mode_map = {
            "NextOpen": aq.ExecutionMode.NextOpen,
            "CurrentClose": aq.ExecutionMode.CurrentClose,
            "NextHighLowMid": aq.ExecutionMode.NextHighLowMid,
            "NextAverage": aq.ExecutionMode.NextAverage,
        }
        
        mode = mode_map.get(mode_str)
        if mode is None:
            logger.warning(f"未知的执行模式 '{mode_str}'，使用默认模式 NextHighLowMid")
            mode = aq.ExecutionMode.NextHighLowMid
        
        return mode
    
    def run(
        self,
        symbol: str,
        strategy_class: Type[BaseStrategy],
        start_date: str,
        end_date: str,
        use_cache: bool = True,
        **strategy_params
    ) -> aq.BacktestResult:
        """
        运行回测
        
        Args:
            symbol: 股票代码（如 "300475"）
            strategy_class: 策略类（必须继承自BaseStrategy）
            start_date: 开始日期，格式 "YYYYMMDD"
            end_date: 结束日期，格式 "YYYYMMDD"
            use_cache: 是否使用数据缓存
            **strategy_params: 策略参数（会传递给策略类的构造函数）
            
        Returns:
            BacktestResult对象
        """
        # 参数校验
        if not issubclass(strategy_class, BaseStrategy):
            raise ValueError(f"策略类必须继承自BaseStrategy")
        
        # 获取数据
        if VERBOSE:
            logger.info(f"开始回测: {symbol} ({start_date} ~ {end_date})")
        
        try:
            data = self.data_manager.get_stock_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                use_cache=use_cache
            )
        except Exception as e:
            logger.error(f"获取数据失败: {str(e)}")
            raise
        
        if data.empty:
            raise ValueError(f"没有获取到任何数据: {symbol} ({start_date} ~ {end_date})")
        
        if VERBOSE:
            logger.info(f"数据准备完成，共 {len(data)} 条记录")
        
        # 实例化策略用于日志描述
        _strategy_for_log = strategy_class(**strategy_params)
        if VERBOSE:
            logger.info(f"使用策略: {_strategy_for_log.get_description()}")
        
        # 运行回测（传入策略实例，akquant支持传入实例）
        try:
            result = aq.run_backtest(
                data=data,
                strategy=strategy_class(**strategy_params),
                initial_cash=self.initial_cash,
                commission_rate=self.commission_rate,
                stamp_tax_rate=self.stamp_tax_rate,
                transfer_fee_rate=self.transfer_fee_rate,
                min_commission=self.min_commission,
                lot_size=self.lot_size,
                execution_mode=self.execution_mode,
                symbol=symbol
            )
            
            if VERBOSE:
                logger.info("回测完成")
            
            return result
            
        except Exception as e:
            logger.error(f"回测执行失败: {str(e)}")
            raise
    
    def compare_strategies(
        self,
        symbol: str,
        strategies: List[Dict],
        start_date: str,
        end_date: str,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        对比多个策略的回测结果
        
        Args:
            symbol: 股票代码
            strategies: 策略配置列表，每个元素为字典，包含：
                - strategy_class: 策略类
                - params: 策略参数字典（可选）
                - name: 策略显示名称（可选）
            start_date: 开始日期
            end_date: 结束日期
            use_cache: 是否使用缓存
            
        Returns:
            对比结果DataFrame
            
        Example:
            strategies = [
                {"strategy_class": MACrossStrategy, "params": {"short_window": 5, "long_window": 20}},
                {"strategy_class": MACDStrategy},
                {"strategy_class": RSIStrategy, "params": {"period": 14}}
            ]
        """
        if VERBOSE:
            logger.info(f"开始对比 {len(strategies)} 个策略")
        
        results = []
        
        for idx, strategy_config in enumerate(strategies):
            strategy_class = strategy_config.get("strategy_class")
            params = strategy_config.get("params", {})
            name = strategy_config.get("name")
            
            if not strategy_class:
                logger.warning(f"策略 {idx+1} 缺少 strategy_class，跳过")
                continue
            
            try:
                # 运行回测
                result = self.run(
                    symbol=symbol,
                    strategy_class=strategy_class,
                    start_date=start_date,
                    end_date=end_date,
                    use_cache=use_cache,
                    **params
                )
                
                # 提取关键指标
                metrics = result.metrics_df
                
                # 策略名称
                if name is None:
                    strategy_instance = strategy_class(**params)
                    name = strategy_instance.get_description()
                
                # 兼容 akquant 0.1.57: metrics_df 列名为 'value' (小写)
                col = "value"
                row = {
                    "策略名称": name,
                    "总收益率(%)": metrics.loc["total_return_pct", col] * 100,
                    "年化收益率(%)": metrics.loc["annualized_return", col] * 100,
                    "最大回撤(%)": metrics.loc["max_drawdown_pct", col] * 100,
                    "夏普比率": metrics.loc["sharpe_ratio", col],
                    "索提诺比率": metrics.loc["sortino_ratio", col],
                    "胜率(%)": metrics.loc["win_rate", col],
                    "交易次数": int(metrics.loc["trade_count", col]),
                    "盈亏比": metrics.loc["profit_factor", col],
                    "卡尔玛比率": metrics.loc["calmar_ratio", col],
                }
                
                results.append(row)
                
            except Exception as e:
                logger.error(f"策略 {idx+1} ({name or strategy_class.__name__}) 回测失败: {str(e)}")
        
        # 转换为DataFrame
        comparison_df = pd.DataFrame(results)
        
        if VERBOSE:
            logger.info("策略对比完成")
        
        return comparison_df