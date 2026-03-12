"""
数据管理模块
负责股票数据的获取、缓存和更新
"""
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import akshare as ak
from config import (
    DATA_CACHE_DIR,
    USE_CACHE_BY_DEFAULT,
    AKSHARE_RETRY_COUNT,
    AKSHARE_REQUEST_INTERVAL,
    CACHE_EXPIRY_DAYS,
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


class DataManager:
    """
    数据管理器
    提供股票数据的获取、缓存和更新功能
    """
    
    def __init__(self, cache_dir: str = DATA_CACHE_DIR):
        """
        初始化数据管理器
        
        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        if VERBOSE:
            logger.info(f"数据管理器初始化完成，缓存目录: {cache_dir}")
    
    def _get_cache_path(self, symbol: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            symbol: 股票代码
            
        Returns:
            缓存文件完整路径
        """
        return os.path.join(self.cache_dir, f"{symbol}.parquet")
    
    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        验证和清洗数据
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            清洗后的DataFrame
        """
        # 兼容中文列名（stock_zh_a_hist）和英文列名（stock_zh_a_daily）
        if '日期' in df.columns:
            df = df.rename(columns={
                '日期': 'date', '开盘': 'open', '最高': 'high',
                '最低': 'low', '收盘': 'close', '成交量': 'volume'
            })
        
        # 检查必需字段
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"数据缺少必需字段: {missing_columns}")
        
        # 过滤异常值
        original_len = len(df)
        df = df[
            (df['open'] > 0) & 
            (df['high'] > 0) & 
            (df['low'] > 0) & 
            (df['close'] > 0) & 
            (df['volume'] >= 0)
        ]
        
        if len(df) < original_len:
            logger.warning(f"过滤了 {original_len - len(df)} 条异常数据")
        
        # 确保日期是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
        
        # 按日期升序排列
        df = df.sort_values('date').reset_index(drop=True)
        
        # 只保留需要的列
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        
        return df
    
    def _fetch_from_akshare(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        从akshare获取数据（带重试机制）
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            
        Returns:
            股票数据DataFrame
        """
        for attempt in range(AKSHARE_RETRY_COUNT):
            try:
                if VERBOSE:
                    logger.info(f"正在从akshare获取 {symbol} 数据: {start_date} ~ {end_date}")
                
                # stock_zh_a_daily 使用 Sina 接口，比东方财富更稳定
                # symbol 需要加市场前缀：深交所 sz，上交所 sh
                if symbol.startswith('6'):
                    full_symbol = f"sh{symbol}"
                elif symbol.startswith(('0', '3')):
                    full_symbol = f"sz{symbol}"
                else:
                    full_symbol = symbol  # 已有前缀或其他情况
                
                df = ak.stock_zh_a_daily(
                    symbol=full_symbol,
                    start_date=start_date,
                    end_date=end_date,
                    adjust=""  # 不复权
                )
                
                if df is None or df.empty:
                    raise ValueError(f"获取到的数据为空")
                
                if VERBOSE:
                    logger.info(f"成功获取 {len(df)} 条数据")
                
                return df
                
            except Exception as e:
                logger.warning(f"第 {attempt + 1} 次获取失败: {str(e)}")
                if attempt < AKSHARE_RETRY_COUNT - 1:
                    # 递增等待：第1次等2s，第2次等5s，降低被服务器拒绝的概率
                    wait = AKSHARE_REQUEST_INTERVAL * (attempt + 1) * 2
                    logger.info(f"等待 {wait}s 后重试...")
                    time.sleep(wait)
                else:
                    raise RuntimeError(f"获取数据失败，已重试 {AKSHARE_RETRY_COUNT} 次: {str(e)}")
    
    def get_stock_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        use_cache: bool = USE_CACHE_BY_DEFAULT
    ) -> pd.DataFrame:
        """
        获取股票数据（优先使用缓存）
        
        Args:
            symbol: 股票代码（如 "300475"）
            start_date: 开始日期，格式 "YYYYMMDD"
            end_date: 结束日期，格式 "YYYYMMDD"
            use_cache: 是否使用缓存
            
        Returns:
            股票数据DataFrame，包含 date/open/high/low/close/volume 列
        """
        cache_path = self._get_cache_path(symbol)
        
        # 转换日期格式
        start_dt = pd.to_datetime(start_date, format='%Y%m%d')
        end_dt = pd.to_datetime(end_date, format='%Y%m%d')
        
        # 检查缓存
        if use_cache and os.path.exists(cache_path):
            try:
                cached_df = pd.read_parquet(cache_path)
                cached_df['date'] = pd.to_datetime(cached_df['date'])
                
                cache_start = cached_df['date'].min()
                cache_end = cached_df['date'].max()
                
                # 如果缓存完全覆盖需要的日期范围
                # end_dt 允许最多7天误差（覆盖周末/节假日无交易日的情况）
                if cache_start <= start_dt and cache_end >= end_dt - timedelta(days=7):
                    if VERBOSE:
                        logger.info(f"使用缓存数据: {symbol}")
                    result_df = cached_df[
                        (cached_df['date'] >= start_dt) & 
                        (cached_df['date'] <= end_dt)
                    ].reset_index(drop=True)
                    return result_df
                else:
                    if VERBOSE:
                        logger.info(f"缓存数据不完整，需要更新: {symbol}")
            except Exception as e:
                logger.warning(f"读取缓存失败: {str(e)}")
        
        # 从akshare获取数据
        df = self._fetch_from_akshare(symbol, start_date, end_date)
        
        # 验证和清洗数据
        df = self._validate_data(df)
        
        # 保存到缓存
        if use_cache:
            try:
                # 如果有旧缓存，合并数据
                if os.path.exists(cache_path):
                    old_df = pd.read_parquet(cache_path)
                    old_df['date'] = pd.to_datetime(old_df['date'])
                    df = pd.concat([old_df, df]).drop_duplicates(subset=['date']).sort_values('date').reset_index(drop=True)
                
                df.to_parquet(cache_path, index=False)
                if VERBOSE:
                    logger.info(f"数据已缓存到: {cache_path}")
            except Exception as e:
                logger.warning(f"保存缓存失败: {str(e)}")
        
        # 返回请求范围内的数据
        result_df = df[
            (df['date'] >= start_dt) & 
            (df['date'] <= end_dt)
        ].reset_index(drop=True)
        
        return result_df
    
    def update_cache(self, symbol: str) -> None:
        """
        更新指定股票的缓存数据（增量更新）
        
        Args:
            symbol: 股票代码
        """
        cache_path = self._get_cache_path(symbol)
        
        if not os.path.exists(cache_path):
            logger.warning(f"{symbol} 缓存不存在，请先调用 get_stock_data")
            return
        
        try:
            # 读取现有缓存
            cached_df = pd.read_parquet(cache_path)
            cached_df['date'] = pd.to_datetime(cached_df['date'])
            
            # 获取最新日期
            last_date = cached_df['date'].max()
            today = datetime.now()
            
            # 如果最新日期就是今天，无需更新
            if last_date.date() >= today.date():
                if VERBOSE:
                    logger.info(f"{symbol} 缓存已是最新")
                return
            
            # 计算更新日期范围
            update_start = (last_date + timedelta(days=1)).strftime('%Y%m%d')
            update_end = today.strftime('%Y%m%d')
            
            if VERBOSE:
                logger.info(f"更新 {symbol} 缓存: {update_start} ~ {update_end}")
            
            # 获取增量数据（今日盘中/未开盘时可能返回空，静默跳过）
            try:
                new_df = self._fetch_from_akshare(symbol, update_start, update_end)
            except Exception:
                if VERBOSE:
                    logger.info(f"{symbol} 增量数据暂不可用（可能今日尚未收盘），使用现有缓存")
                return

            if new_df is None or new_df.empty:
                if VERBOSE:
                    logger.info(f"{symbol} 无新增数据")
                return
            
            # 验证和清洗
            new_df = self._validate_data(new_df)
            
            # 合并数据
            updated_df = pd.concat([cached_df, new_df]).drop_duplicates(subset=['date']).sort_values('date').reset_index(drop=True)
            
            # 保存
            updated_df.to_parquet(cache_path, index=False)
            if VERBOSE:
                logger.info(f"{symbol} 缓存更新完成，新增 {len(new_df)} 条数据")
            
        except Exception as e:
            logger.error(f"更新缓存失败: {str(e)}")
            raise
    
    def clear_cache(self, symbol: Optional[str] = None) -> None:
        """
        清除缓存数据
        
        Args:
            symbol: 股票代码，如果为None则清除所有缓存
        """
        if symbol:
            cache_path = self._get_cache_path(symbol)
            if os.path.exists(cache_path):
                os.remove(cache_path)
                logger.info(f"已清除 {symbol} 的缓存")
            else:
                logger.warning(f"{symbol} 缓存不存在")
        else:
            # 清除所有缓存
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.parquet')]
            for cache_file in cache_files:
                os.remove(os.path.join(self.cache_dir, cache_file))
            logger.info(f"已清除所有缓存，共 {len(cache_files)} 个文件")
    
    def list_cached_stocks(self) -> list:
        """
        列出所有已缓存的股票
        
        Returns:
            股票代码列表
        """
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.parquet')]
        symbols = [f.replace('.parquet', '') for f in cache_files]
        return symbols