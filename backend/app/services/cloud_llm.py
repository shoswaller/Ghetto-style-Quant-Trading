"""
云端LLM服务 - 通过环境变量配置
"""
import os
import httpx
from typing import Optional


class CloudLLM:
    """云端LLM封装（默认使用DeepSeek，支持兼容OpenAI格式的API）"""
    
    def __init__(self):
        self.api_key = os.environ.get('CLOUD_API_KEY', '')
        self.base_url = os.environ.get('CLOUD_BASE_URL', 'https://api.deepseek.com')
        self.model = os.environ.get('CLOUD_MODEL', 'deepseek-chat')
        self.timeout = 60
        self.max_tokens = 2000
        self.temperature = 0.7
    
    @property
    def enabled(self) -> bool:
        """检查是否配置了API密钥"""
        return bool(self.api_key)
    
    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        调用云端LLM生成回复
        
        Args:
            prompt: 用户输入
            system_prompt: 系统提示词（可选）
            
        Returns:
            LLM生成的内容
        """
        if not self.enabled:
            raise RuntimeError("未配置 CLOUD_API_KEY 环境变量")
        
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
        except httpx.TimeoutException:
            raise RuntimeError(f"云端LLM请求超时（{self.timeout}秒）")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"云端LLM请求失败: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"云端LLM调用错误: {str(e)}")
    
    def health_check(self) -> bool:
        """检查云端LLM服务是否可用"""
        if not self.enabled:
            return False
        
        try:
            # 发送一个简单的测试请求
            result = self.complete("Hello", system_prompt="Reply with 'OK' only.")
            return True
        except:
            return False


# 单例
cloud_llm = CloudLLM()
