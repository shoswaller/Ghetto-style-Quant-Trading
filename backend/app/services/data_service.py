"""
数据获取服务 - 使用AKShare获取股票数据
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np


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
            print(f"获取股票信息失败: {e}")
            return None
    
    def get_realtime_quote(self, code: str) -> Optional[Dict]:
        """
        获取实时行情
        
        Args:
            code: 股票代码
            
        Returns:
            实时行情数据
        """
        try:
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
            if stock.empty:
                return None
            
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
            print(f"获取实时行情失败: {e}")
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
            print(f"获取日线数据失败: {e}")
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
        macd, signal, hist = self._calc_macd(close)
        macd_signal = "金叉" if hist > 0 and len(df) > 1 else "死叉"
        
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
            df = ak.stock_individual_fund_flow(symbol=code, market="sh" if code.startswith('6') else "sz")
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
            print(f"获取资金流向失败: {e}")
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
        """计算MACD"""
        if len(prices) < slow:
            return None, None, None
        
        # 计算EMA
        ema_fast = self._calc_ema(prices, fast)
        ema_slow = self._calc_ema(prices, slow)
        
        if ema_fast is None or ema_slow is None:
            return None, None, None
        
        macd_line = ema_fast - ema_slow
        
        # 简化计算，取最后一个值
        return float(macd_line), 0, float(macd_line)
    
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
