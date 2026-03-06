"""
结果分析模块
提供回测结果的分析、展示和报告生成功能
"""
import os
import logging
from typing import Dict, Optional
import pandas as pd
import akquant as aq
from config import REPORTS_DIR, LOG_LEVEL, VERBOSE

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class Analyzer:
    """
    回测结果分析器
    提供结果展示、报告生成和指标对比功能
    """
    
    def __init__(self, reports_dir: str = REPORTS_DIR):
        """
        初始化分析器
        
        Args:
            reports_dir: 报告输出目录
        """
        self.reports_dir = reports_dir
        os.makedirs(reports_dir, exist_ok=True)
    
    def print_summary(self, result: aq.BacktestResult, strategy_name: str = "策略") -> None:
        """
        打印回测结果摘要
        
        Args:
            result: BacktestResult对象
            strategy_name: 策略名称
        """
        metrics = result.metrics_df
        
        print("\n" + "="*60)
        print(f"{'回测结果摘要':^56}")
        print("="*60)
        
        # 基本信息
        print(f"\n【策略信息】")
        # 兼容 akquant 0.1.57: metrics_df 列名为 'value' (小写)
        col = 'value'
        print(f"策略名称: {strategy_name}")
        print(f"回测区间: {metrics.loc['start_time', col]} ~ {metrics.loc['end_time', col]}")
        print(f"回测天数: {metrics.loc['duration', col]}")
        print(f"K线数量: {int(metrics.loc['total_bars', col])} 根")
        
        # 收益指标
        print(f"\n【收益指标】")
        print(f"初始资金: {metrics.loc['initial_market_value', col]:,.2f} 元")
        print(f"最终权益: {metrics.loc['end_market_value', col]:,.2f} 元")
        print(f"总收益: {metrics.loc['total_pnl', col]:,.2f} 元")
        print(f"总收益率: {metrics.loc['total_return_pct', col]*100:.2f}%")
        print(f"年化收益率: {metrics.loc['annualized_return', col]*100:.2f}%")
        
        # 风险指标
        print(f"\n【风险指标】")
        print(f"最大回撤: {metrics.loc['max_drawdown_pct', col]*100:.2f}%")
        print(f"波动率: {metrics.loc['volatility', col]*100:.2f}%")
        print(f"夏普比率: {metrics.loc['sharpe_ratio', col]:.2f}")
        print(f"索提诺比率: {metrics.loc['sortino_ratio', col]:.2f}")
        print(f"卡尔玛比率: {metrics.loc['calmar_ratio', col]:.2f}")
        
        # 交易指标
        print(f"\n【交易指标】")
        print(f"交易次数: {int(metrics.loc['trade_count', col])} 笔")
        print(f"胜率: {metrics.loc['win_rate', col]:.2f}%")
        print(f"盈利次数: {int(metrics.loc['winning_trades', col])} 笔")
        print(f"亏损次数: {int(metrics.loc['losing_trades', col])} 笔")
        print(f"盈亏比: {metrics.loc['profit_factor', col]:.2f}")
        print(f"平均盈利: {metrics.loc['avg_profit', col]:,.2f} 元")
        print(f"平均亏损: {metrics.loc['avg_loss', col]:,.2f} 元")
        
        # 其他指标
        print(f"\n【其他指标】")
        print(f"总手续费: {metrics.loc['total_commission', col]:,.2f} 元")
        print(f"平均持仓天数: {metrics.loc['avg_trade_bars', col]:.1f} 天")
        print(f"市场暴露时间: {metrics.loc['exposure_time_pct', col]:.2f}%")
        print(f"系统质量指数(SQN): {metrics.loc['sqn', col]:.2f}")
        
        print("="*60 + "\n")
    
    def save_report(
        self,
        result: aq.BacktestResult,
        filename: Optional[str] = None,
        show: bool = True
    ) -> str:
        """
        生成并保存HTML回测报告
        
        Args:
            result: BacktestResult对象
            filename: 报告文件名（不含路径），默认为 "backtest_report.html"
            show: 是否自动在浏览器中打开报告
            
        Returns:
            报告文件的完整路径
        """
        if filename is None:
            filename = "backtest_report.html"
        
        # 确保文件名以.html结尾
        if not filename.endswith('.html'):
            filename += '.html'
        
        # 完整路径
        filepath = os.path.join(self.reports_dir, filename)
        
        try:
            # report(title, filename, show) - akquant 0.1.57 API
            result.report(filename=filepath, show=show)
            
            if VERBOSE:
                logger.info(f"报告已保存到: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"生成报告失败: {str(e)}")
            raise
    
    def compare_metrics(
        self,
        results: Dict[str, aq.BacktestResult],
        key_metrics: Optional[list] = None
    ) -> pd.DataFrame:
        """
        对比多个回测结果的关键指标
        
        Args:
            results: 回测结果字典，key为策略名称，value为BacktestResult对象
            key_metrics: 要对比的指标列表，默认为常用核心指标
            
        Returns:
            对比结果DataFrame
        """
        if key_metrics is None:
            key_metrics = [
                "total_return_pct",
                "annualized_return",
                "max_drawdown_pct",
                "sharpe_ratio",
                "sortino_ratio",
                "calmar_ratio",
                "win_rate",
                "trade_count",
                "profit_factor",
                "avg_trade_bars",
            ]
        
        # 指标中文名称映射
        metric_names = {
            "total_return_pct": "总收益率(%)",
            "annualized_return": "年化收益率(%)",
            "max_drawdown_pct": "最大回撤(%)",
            "sharpe_ratio": "夏普比率",
            "sortino_ratio": "索提诺比率",
            "calmar_ratio": "卡尔玛比率",
            "win_rate": "胜率(%)",
            "trade_count": "交易次数",
            "profit_factor": "盈亏比",
            "avg_trade_bars": "平均持仓天数",
        }
        
        comparison_data = {}
        
        for strategy_name, result in results.items():
            metrics = result.metrics_df
            strategy_metrics = {}
            
            col = 'value'
            for metric in key_metrics:
                if metric in metrics.index:
                    value = metrics.loc[metric, col]
                    
                    # 百分比指标转换
                    if metric in ["total_return_pct", "annualized_return", "max_drawdown_pct"]:
                        value = value * 100
                    
                    strategy_metrics[metric_names.get(metric, metric)] = value
            
            comparison_data[strategy_name] = strategy_metrics
        
        # 转换为DataFrame
        comparison_df = pd.DataFrame(comparison_data).T
        
        # 格式化显示
        comparison_df = comparison_df.round(2)
        
        if VERBOSE:
            logger.info("策略对比完成")
        
        return comparison_df
    
    def print_comparison(self, comparison_df: pd.DataFrame) -> None:
        """
        打印策略对比结果
        
        Args:
            comparison_df: 对比结果DataFrame
        """
        print("\n" + "="*80)
        print(f"{'策略对比':^76}")
        print("="*80)
        print(comparison_df.to_string())
        print("="*80 + "\n")
    
    def save_comparison(
        self,
        comparison_df: pd.DataFrame,
        filename: str = "strategy_comparison.csv"
    ) -> str:
        """
        保存策略对比结果到CSV文件
        
        Args:
            comparison_df: 对比结果DataFrame
            filename: 文件名
            
        Returns:
            文件完整路径
        """
        filepath = os.path.join(self.reports_dir, filename)
        
        try:
            comparison_df.to_csv(filepath, encoding='utf-8-sig')
            
            if VERBOSE:
                logger.info(f"对比结果已保存到: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"保存对比结果失败: {str(e)}")
            raise