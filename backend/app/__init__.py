"""
丐版量化交易系统 - Flask应用初始化
"""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_name='default'):
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    from app.config import config
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    from app.api import stock_bp, analysis_bp
    app.register_blueprint(stock_bp, url_prefix='/api/stock')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 健康检查路由
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': '丐版量化交易系统运行中'}
    
    return app
