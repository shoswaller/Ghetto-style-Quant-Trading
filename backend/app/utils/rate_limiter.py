"""
频率限制器 - 预留接口，初期不启用
"""
import time
from collections import deque
from threading import Lock


class RateLimiter:
    """
    频率限制器
    
    初期不启用，保留接口供后续扩展
    """
    
    def __init__(self, enabled: bool = False, max_calls_per_minute: int = 60):
        """
        初始化频率限制器
        
        Args:
            enabled: 是否启用
            max_calls_per_minute: 每分钟最大调用次数
        """
        self.enabled = enabled
        self.max_calls = max_calls_per_minute
        self.call_history: deque = deque()
        self.lock = Lock()
    
    def check_limit(self) -> bool:
        """
        检查是否超过频率限制
        
        Returns:
            True: 未超限，可以调用
            False: 已超限，需要等待
        """
        if not self.enabled:
            return True  # 未启用时总是放行
        
        with self.lock:
            now = time.time()
            
            # 清理一分钟前的记录
            while self.call_history and self.call_history[0] < now - 60:
                self.call_history.popleft()
            
            # 检查是否超限
            if len(self.call_history) >= self.max_calls:
                return False
            
            return True
    
    def record_call(self):
        """记录一次调用"""
        if not self.enabled:
            return
        
        with self.lock:
            self.call_history.append(time.time())
    
    def wait_if_needed(self) -> float:
        """
        如果需要等待，返回等待时间
        
        Returns:
            需要等待的秒数，0表示无需等待
        """
        if not self.enabled:
            return 0
        
        with self.lock:
            now = time.time()
            
            # 清理过期记录
            while self.call_history and self.call_history[0] < now - 60:
                self.call_history.popleft()
            
            if len(self.call_history) >= self.max_calls:
                # 计算需要等待的时间
                oldest = self.call_history[0]
                wait_time = 60 - (now - oldest)
                return max(0, wait_time)
            
            return 0
    
    def enable(self, max_calls_per_minute: int = 60):
        """
        启用频率限制
        
        Args:
            max_calls_per_minute: 每分钟最大调用次数
        """
        self.enabled = True
        self.max_calls = max_calls_per_minute
    
    def disable(self):
        """禁用频率限制"""
        self.enabled = False
    
    def get_stats(self) -> dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        with self.lock:
            now = time.time()
            
            # 清理过期记录
            while self.call_history and self.call_history[0] < now - 60:
                self.call_history.popleft()
            
            return {
                'enabled': self.enabled,
                'max_calls_per_minute': self.max_calls,
                'current_calls_in_window': len(self.call_history),
                'remaining_calls': max(0, self.max_calls - len(self.call_history))
            }


# 全局实例
# 云端LLM限制器
cloud_llm_limiter = RateLimiter(enabled=False, max_calls_per_minute=60)

# 局域网LLM限制器
local_llm_limiter = RateLimiter(enabled=False, max_calls_per_minute=120)
