"""
配置管理模块

云端LLM配置：通过环境变量
局域网LLM配置：通过配置文件
"""
import os
import json
from pathlib import Path


def load_json_config(config_path: str) -> dict:
    """加载JSON配置文件"""
    full_path = Path(__file__).parent.parent / config_path
    if full_path.exists():
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


class BaseConfig:
    """基础配置"""
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ghetto-quant-secret-key')
    
    # 数据库配置
    BASE_DIR = Path(__file__).parent.parent.parent
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR / "data" / "quant.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 云端LLM配置 - 从环境变量读取
    CLOUD_LLM_API_KEY = os.environ.get('CLOUD_API_KEY', '')
    CLOUD_LLM_BASE_URL = os.environ.get('CLOUD_BASE_URL', 'https://api.deepseek.com')
    CLOUD_LLM_MODEL = os.environ.get('CLOUD_MODEL', 'deepseek-chat')
    
    # 备选云端LLM
    MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', '')
    KIMI_API_KEY = os.environ.get('KIMI_API_KEY', '')
    
    # 局域网LLM配置 - 从配置文件读取
    LOCAL_LLM_CONFIG = load_json_config('config/llm_config.json')
    
    # 缓存配置
    CACHE_CONFIG = LOCAL_LLM_CONFIG.get('cache', {
        'memory_cache_size': 1000,
        'memory_cache_ttl': 300
    })


class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(BaseConfig):
    """生产环境配置"""
    DEBUG = False
    TESTING = False


class TestingConfig(BaseConfig):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
