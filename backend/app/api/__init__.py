"""
API路由模块
"""
from app.api.stock import stock_bp
from app.api.analysis import analysis_bp

__all__ = ['stock_bp', 'analysis_bp']
