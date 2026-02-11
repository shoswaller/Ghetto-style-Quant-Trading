"""
数据获取服务 - 使用AKShare获取股票数据
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import numpy as np
import logging
import time
import hashlib
from functools import wraps

logger = logging.getLogger(__name__)


def cached_with_ttl(ttl_seconds: int = 60):
    """简单的TTL缓存装饰器"""
    cache = {}
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键（跳过self参数）
            key = f"{func.__name__}:{str(args[1:])}:{str(kwargs)}"
            cache_key = hashlib.md5(key.encode()).hexdigest()
            
            now = time.time()
            
            # 检查缓存
            if cache_key in cache:
                result, expire_time = cache[cache_key]
                if now < expire_time:
                    logger.debug(f"缓存命中: {func.__name__}")
                    return result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            if result is not None:
                cache[cache_key] = (result, now + ttl_seconds)
            
            # 清理过期缓存（简单策略）
            if len(cache) > 100:
                expired_keys = [k for k, (_, exp) in cache.items() if now > exp]
                for k in expired_keys:
                    del cache[k]
            
            return result
        return wrapper
    return decorator


class DataService:
    """股票数据获取服务"""
    
    def __init__(self):
        pass
    
    def get_stock_info(self, code: str) -> Optional[Dict]:
        """
        获取股票基本信息
        
        Args:
            code: 股票代码，如 "000001"
            
        Returns:
            股票信息字典
        """
        try:
            # 获取个股信息
            df = ak.stock_individual_info_em(symbol=code)
            info = {}
            for _, row in df.iterrows():
                info[row['item']] = row['value']
            print(info.get('股票简称', ''),code,'',df)
            return {
                'code': code,
                'name': info.get('股票简称', ''),
                'industry': info.get('行业', ''),
                'market': self._get_market(code),
                'total_value': info.get('总市值', ''),
                'circulating_value': info.get('流通市值', ''),
                'pe_ratio': info.get('市盈率(动态)', ''),
                'pb_ratio': info.get('市净率', '')
            }
        except Exception as e:
            logger.error(f"获取股票信息失败 [{code}]: {e}")
            return None
    
    @cached_with_ttl(ttl_seconds=30)
    def get_realtime_quote(self, code: str) -> Optional[Dict]:
        """
        获取实时行情（带30秒缓存）
        
        Args:
            code: 股票代码
            
        Returns:
            实时行情数据
        """
        # 尝试多个数据源，带重试机制
        for attempt in range(2):
            try:
                # 方法1：使用 stock_zh_a_spot_em
                df = ak.stock_zh_a_spot_em()
                stock = df[df['代码'] == code]
                if not stock.empty:
                    row = stock.iloc[0]
                    return {
                        'code': code,
                        'name': row['名称'],
                        'current_price': float(row['最新价']),
                        'change_pct': float(row['涨跌幅']),
                        'change_amount': float(row['涨跌额']),
                        'volume': float(row['成交量']),
                        'amount': float(row['成交额']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'open': float(row['今开']),
                        'prev_close': float(row['昨收']),
                        'turnover': float(row['换手率']) if pd.notna(row['换手率']) else 0,
                        'amplitude': float(row['振幅']) if pd.notna(row['振幅']) else 0
                    }
            except Exception as e:
                logger.warning(f"获取实时行情尝试 {attempt + 1} 失败 [{code}]: {e}")
                if attempt == 0:
                    time.sleep(1)  # 等待1秒后重试
                continue
        
        # 方法2：从日线数据获取最新价格作为备选
        try:
            daily = self.get_daily_data(code, days=1)
            if daily:
                latest = daily[-1]
                return {
                    'code': code,
                    'name': '',  # 从其他接口获取
                    'current_price': latest['close'],
                    'change_pct': latest['change_pct'],
                    'change_amount': 0,
                    'volume': latest['volume'],
                    'amount': latest['amount'],
                    'high': latest['high'],
                    'low': latest['low'],
                    'open': latest['open'],
                    'prev_close': 0,
                    'turnover': latest.get('turnover', 0),
                    'amplitude': 0
                }
        except Exception as e2:
            logger.error(f"备选实时行情也失败 [{code}]: {e2}")
        
        logger.error(f"获取实时行情失败 [{code}]: 所有尝试均失败")
        return None
    
    def get_daily_data(self, code: str, days: int = 60) -> List[Dict]:
        """
        获取日线历史数据
        
        Args:
            code: 股票代码
            days: 获取天数，默认60天
            
        Returns:
            日线数据列表
        """
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                adjust="qfq"  # 前复权
            )
            
            # 取最近N天的数据
            df = df.tail(days)
            
            result = []
            for _, row in df.iterrows():
                result.append({
                    'trade_date': row['日期'],
                    'open': float(row['开盘']),
                    'close': float(row['收盘']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'volume': float(row['成交量']),
                    'amount': float(row['成交额']),
                    'change_pct': float(row['涨跌幅']),
                    'turnover': float(row['换手率']) if pd.notna(row['换手率']) else 0
                })
            
            return result
        except Exception as e:
            logger.error(f"获取日线数据失败 [{code}]: {e}")
            return []
    
    def get_technical_indicators(self, code: str, days: int = 60) -> Dict:
        """
        计算技术指标
        
        Args:
            code: 股票代码
            days: 计算天数
            
        Returns:
            技术指标字典
        """
        daily_data = self.get_daily_data(code, days)
        if not daily_data:
            return {}
        
        df = pd.DataFrame(daily_data)
        close = df['close'].values
        
        # 计算均线
        ma5 = self._calc_ma(close, 5)
        ma10 = self._calc_ma(close, 10)
        ma20 = self._calc_ma(close, 20)
        
        # 计算MACD
        macd, signal, hist, macd_signal = self._calc_macd(close)
        
        # 计算KDJ
        k, d, j = self._calc_kdj(df)
        kdj_signal = "超买" if k > 80 else ("超卖" if k < 20 else "中性")
        
        # 计算RSI
        rsi = self._calc_rsi(close)
        
        return {
            'ma5': round(ma5, 2) if ma5 else None,
            'ma10': round(ma10, 2) if ma10 else None,
            'ma20': round(ma20, 2) if ma20 else None,
            'macd': {
                'value': round(macd, 4) if macd else None,
                'signal': macd_signal
            },
            'kdj': {
                'k': round(k, 2) if k else None,
                'd': round(d, 2) if d else None,
                'j': round(j, 2) if j else None,
                'signal': kdj_signal
            },
            'rsi': round(rsi, 2) if rsi else None
        }
    
    def get_fund_flow(self, code: str) -> Optional[Dict]:
        """
        获取资金流向数据
        
        Args:
            code: 股票代码
            
        Returns:
            资金流向数据
        """
        try:
            # AKShare API 更新：使用 stock 参数而非 symbol
            df = ak.stock_individual_fund_flow(
                stock=code, 
                market="sh" if code.startswith('6') else "sz"
            )
            if df.empty:
                return None
            
            # 取最近一天的数据
            row = df.iloc[-1]
            return {
                'date': str(row['日期']),
                'main_net_inflow': float(row['主力净流入-净额']) if pd.notna(row['主力净流入-净额']) else 0,
                'main_net_inflow_pct': float(row['主力净流入-净占比']) if pd.notna(row['主力净流入-净占比']) else 0,
                'retail_net_inflow': float(row['散户净流入-净额']) if pd.notna(row.get('散户净流入-净额', 0)) else 0
            }
        except Exception as e:
            logger.error(f"获取资金流向失败 [{code}]: {e}")
            return None
    
    def _get_market(self, code: str) -> str:
        """判断股票所属市场"""
        if code.startswith('6'):
            return 'SH'
        elif code.startswith(('0', '3')):
            return 'SZ'
        elif code.startswith(('4', '8')):
            return 'BJ'
        return 'Unknown'
    
    def _calc_ma(self, prices, period: int) -> Optional[float]:
        """计算移动平均线"""
        if len(prices) < period:
            return None
        return float(np.mean(prices[-period:]))
    
    def _calc_macd(self, prices, fast=12, slow=26, signal=9):
        """
        计算MACD指标
        
        Returns:
            (macd_line, signal_line, histogram, signal_text)
        """
        if len(prices) < slow + signal:
            return None, None, None, "数据不足"
        
        prices_series = pd.Series(prices)
        
        # 计算EMA
        ema_fast = prices_series.ewm(span=fast, adjust=False).mean()
        ema_slow = prices_series.ewm(span=slow, adjust=False).mean()
        
        # MACD线 = 快线EMA - 慢线EMA
        macd_line = ema_fast - ema_slow
        
        # Signal线 = MACD的EMA
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        
        # Histogram = MACD - Signal
        histogram = macd_line - signal_line
        
        # 判断金叉/死叉
        hist_values = histogram.values
        if len(hist_values) >= 2:
            if hist_values[-2] < 0 and hist_values[-1] > 0:
                signal_text = "金叉"
            elif hist_values[-2] > 0 and hist_values[-1] < 0:
                signal_text = "死叉"
            else:
                signal_text = "多头" if hist_values[-1] > 0 else "空头"
        else:
            signal_text = "中性"
        
        return (
            float(macd_line.iloc[-1]),
            float(signal_line.iloc[-1]),
            float(histogram.iloc[-1]),
            signal_text
        )
    
    def _calc_ema(self, prices, period: int) -> Optional[float]:
        """计算指数移动平均"""
        if len(prices) < period:
            return None
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def _calc_kdj(self, df, n=9, m1=3, m2=3):
        """计算KDJ指标"""
        if len(df) < n:
            return None, None, None
        
        low_list = df['low'].rolling(n, min_periods=n).min()
        high_list = df['high'].rolling(n, min_periods=n).max()
        
        rsv = (df['close'] - low_list) / (high_list - low_list) * 100
        rsv = rsv.fillna(50)
        
        k = rsv.ewm(com=m1-1, adjust=False).mean()
        d = k.ewm(com=m2-1, adjust=False).mean()
        j = 3 * k - 2 * d
        
        return float(k.iloc[-1]), float(d.iloc[-1]), float(j.iloc[-1])
    
    def _calc_rsi(self, prices, period: int = 14) -> Optional[float]:
        """计算RSI指标"""
        if len(prices) < period + 1:
            return None
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)


# 单例
data_service = DataService()
