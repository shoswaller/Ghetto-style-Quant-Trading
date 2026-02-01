"""
局域网LLM服务 - 通过llama.cpp server调用
"""
import httpx
from typing import Optional
from flask import current_app


class LocalLLM:
    """局域网LLM封装（llama.cpp server）"""
    
    def __init__(self):
        self._config = None
    
    @property
    def config(self) -> dict:
        """获取局域网LLM配置"""
        if self._config is None:
            try:
                from app.config import BaseConfig
                self._config = BaseConfig.LOCAL_LLM_CONFIG.get('local_llm', {})
            except:
                self._config = {}
        return self._config
    
    @property
    def enabled(self) -> bool:
        return self.config.get('enabled', False)
    
    @property
    def api_url(self) -> str:
        return self.config.get('api_url', 'http://localhost:8080')
    
    @property
    def api_key(self) -> str:
        return self.config.get('api_key', '')
    
    @property
    def timeout(self) -> int:
        return self.config.get('timeout', 120)
    
    @property
    def max_tokens(self) -> int:
        return self.config.get('max_tokens', 4096)
    
    @property
    def temperature(self) -> float:
        return self.config.get('temperature', 0.7)
    
    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        调用局域网LLM生成回复
        
        Args:
            prompt: 用户输入
            system_prompt: 系统提示词（可选）
            
        Returns:
            LLM生成的内容
        """
        if not self.enabled:
            raise RuntimeError("局域网LLM未启用，请检查配置文件")
        
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # llama.cpp server 兼容 OpenAI API 格式
        payload = {
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.api_url}/v1/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
        except httpx.TimeoutException:
            raise RuntimeError(f"局域网LLM请求超时（{self.timeout}秒）")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"局域网LLM请求失败: {e.response.status_code}")
        except Exception as e:
            raise RuntimeError(f"局域网LLM调用错误: {str(e)}")
    
    def health_check(self) -> bool:
        """检查局域网LLM服务是否可用"""
        if not self.enabled:
            return False
        
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self.api_url}/health")
                return response.status_code == 200
        except:
            return False


# 单例
local_llm = LocalLLM()
