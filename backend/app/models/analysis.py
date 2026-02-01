"""
分析结果模型
"""
from datetime import datetime
from app import db


class AnalysisCache(db.Model):
    """分析结果缓存表"""
    __tablename__ = 'analysis_cache'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), db.ForeignKey('stock.code'), nullable=False, comment='股票代码')
    analysis_type = db.Column(db.String(20), nullable=False, comment='分析类型: daily/weekly/longterm')
    data_hash = db.Column(db.String(64), comment='数据指纹，用于判断缓存有效性')
    prompt = db.Column(db.Text, comment='使用的Prompt')
    result = db.Column(db.Text, comment='分析结果(JSON格式)')
    created_at = db.Column(db.DateTime, default=datetime.now)
    expires_at = db.Column(db.DateTime, comment='过期时间')
    
    __table_args__ = (
        db.Index('idx_analysis_cache_code', 'code'),
        db.Index('idx_analysis_cache_type', 'analysis_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'analysis_type': self.analysis_type,
            'data_hash': self.data_hash,
            'result': self.result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def is_expired(self) -> bool:
        """检查缓存是否过期"""
        if not self.expires_at:
            return True
        return datetime.now() > self.expires_at


class UserOperation(db.Model):
    """用户操作记录表"""
    __tablename__ = 'user_operation'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), db.ForeignKey('stock.code'), nullable=False, comment='股票代码')
    operation_type = db.Column(db.String(20), nullable=False, comment='操作类型: buy/sell/watch')
    price = db.Column(db.Float, comment='操作价格')
    quantity = db.Column(db.Integer, comment='数量')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'operation_type': self.operation_type,
            'price': self.price,
            'quantity': self.quantity,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
