"""
缓存服务 - 两级缓存策略
L1: 内存缓存 (cachetools.TTLCache)
L2: SQLite数据库 (analysis_cache表)
"""
from cachetools import TTLCache
from hashlib import md5
from datetime import datetime, timedelta
from typing import Optional
import json


class CacheService:
    """缓存服务"""
    
    def __init__(self):
        # 从配置加载缓存参数
        try:
            from app.config import BaseConfig
            cache_config = BaseConfig.CACHE_CONFIG
        except:
            cache_config = {}
        
        # L1: 内存缓存
        self.memory_cache = TTLCache(
            maxsize=cache_config.get('memory_cache_size', 1000),
            ttl=cache_config.get('memory_cache_ttl', 300)  # 5分钟
        )
        
        # 缓存过期配置
        self.daily_expire_hour = cache_config.get('daily_expire_hour', 15)
        self.daily_expire_minute = cache_config.get('daily_expire_minute', 30)
        self.weekly_expire_day = cache_config.get('weekly_expire_day', 6)  # 周日
        self.longterm_expire_days = cache_config.get('longterm_expire_days', 7)
    
    def _make_key(self, code: str, analysis_type: str, data_hash: str) -> str:
        """生成缓存键"""
        return f"{code}:{analysis_type}:{data_hash}"
    
    def make_data_hash(self, close_price: float, volume: float, date: str) -> str:
        """
        生成数据指纹，用于判断缓存是否有效
        
        Args:
            close_price: 最新收盘价
            volume: 最新成交量
            date: 日期
            
        Returns:
            数据指纹(MD5)
        """
        data_str = f"{close_price}:{volume}:{date}"
        return md5(data_str.encode()).hexdigest()[:16]
    
    def get(self, code: str, analysis_type: str, data_hash: str) -> Optional[dict]:
        """
        获取缓存
        
        Args:
            code: 股票代码
            analysis_type: 分析类型
            data_hash: 数据指纹
            
        Returns:
            缓存的分析结果，未命中返回None
        """
        key = self._make_key(code, analysis_type, data_hash)
        
        # 先查L1内存缓存
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # 再查L2数据库缓存
        cached = self._get_from_db(code, analysis_type, data_hash)
        if cached:
            # 回填L1缓存
            self.memory_cache[key] = cached
            return cached
        
        return None
    
    def set(self, code: str, analysis_type: str, data_hash: str, 
            result: dict, prompt: str = None):
        """
        设置缓存
        
        Args:
            code: 股票代码
            analysis_type: 分析类型
            data_hash: 数据指纹
            result: 分析结果
            prompt: 使用的Prompt
        """
        key = self._make_key(code, analysis_type, data_hash)
        
        # 设置L1
        self.memory_cache[key] = result
        
        # 设置L2
        expires_at = self._calc_expiry(analysis_type)
        self._save_to_db(code, analysis_type, data_hash, result, prompt, expires_at)
    
    def invalidate(self, code: str, analysis_type: str = None):
        """
        清除指定股票的缓存
        
        Args:
            code: 股票代码
            analysis_type: 分析类型（可选，不传则清除所有类型）
        """
        # 清除L1缓存
        keys_to_remove = []
        for key in self.memory_cache.keys():
            if key.startswith(f"{code}:"):
                if analysis_type is None or key.startswith(f"{code}:{analysis_type}:"):
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.memory_cache[key]
        
        # 清除L2缓存
        self._delete_from_db(code, analysis_type)
    
    def _calc_expiry(self, analysis_type: str) -> datetime:
        """
        计算过期时间
        
        Args:
            analysis_type: 分析类型
            
        Returns:
            过期时间
        """
        now = datetime.now()
        
        if analysis_type == 'daily':
            # 当日收盘后过期（15:30）
            expiry = now.replace(
                hour=self.daily_expire_hour, 
                minute=self.daily_expire_minute, 
                second=0, 
                microsecond=0
            )
            if now >= expiry:
                # 已过收盘时间，设置为明天
                expiry += timedelta(days=1)
            return expiry
        
        elif analysis_type == 'weekly':
            # 本周日过期
            days_until_expire = self.weekly_expire_day - now.weekday()
            if days_until_expire <= 0:
                days_until_expire += 7
            return now + timedelta(days=days_until_expire)
        
        else:
            # 长线分析7天后过期
            return now + timedelta(days=self.longterm_expire_days)
    
    def _get_from_db(self, code: str, analysis_type: str, data_hash: str) -> Optional[dict]:
        """从数据库获取缓存"""
        try:
            from app import db
            from app.models.analysis import AnalysisCache
            
            cached = AnalysisCache.query.filter_by(
                code=code,
                analysis_type=analysis_type,
                data_hash=data_hash
            ).first()
            
            if cached and not cached.is_expired():
                return json.loads(cached.result)
            
            return None
        except Exception as e:
            print(f"从数据库获取缓存失败: {e}")
            return None
    
    def _save_to_db(self, code: str, analysis_type: str, data_hash: str,
                    result: dict, prompt: str, expires_at: datetime):
        """保存缓存到数据库"""
        try:
            from app import db
            from app.models.analysis import AnalysisCache
            
            # 先删除旧缓存
            AnalysisCache.query.filter_by(
                code=code,
                analysis_type=analysis_type
            ).delete()
            
            # 创建新缓存
            cache = AnalysisCache(
                code=code,
                analysis_type=analysis_type,
                data_hash=data_hash,
                prompt=prompt,
                result=json.dumps(result, ensure_ascii=False),
                expires_at=expires_at
            )
            
            db.session.add(cache)
            db.session.commit()
        except Exception as e:
            print(f"保存缓存到数据库失败: {e}")
    
    def _delete_from_db(self, code: str, analysis_type: str = None):
        """从数据库删除缓存"""
        try:
            from app import db
            from app.models.analysis import AnalysisCache
            
            query = AnalysisCache.query.filter_by(code=code)
            if analysis_type:
                query = query.filter_by(analysis_type=analysis_type)
            
            query.delete()
            db.session.commit()
        except Exception as e:
            print(f"从数据库删除缓存失败: {e}")


# 单例
cache_service = CacheService()
