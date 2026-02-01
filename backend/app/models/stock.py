"""
股票数据模型
"""
from datetime import datetime
from app import db


class Stock(db.Model):
    """股票基本信息表"""
    __tablename__ = 'stock'
    
    code = db.Column(db.String(10), primary_key=True, comment='股票代码')
    name = db.Column(db.String(50), nullable=False, comment='股票名称')
    industry = db.Column(db.String(50), comment='所属行业')
    market = db.Column(db.String(10), comment='市场(SH/SZ/BJ)')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    daily_data = db.relationship('StockDaily', backref='stock', lazy='dynamic')
    
    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'industry': self.industry,
            'market': self.market,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class StockDaily(db.Model):
    """股票日线数据表"""
    __tablename__ = 'stock_daily'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), db.ForeignKey('stock.code'), nullable=False, comment='股票代码')
    trade_date = db.Column(db.Date, nullable=False, comment='交易日期')
    open = db.Column(db.Float, comment='开盘价')
    close = db.Column(db.Float, comment='收盘价')
    high = db.Column(db.Float, comment='最高价')
    low = db.Column(db.Float, comment='最低价')
    volume = db.Column(db.Float, comment='成交量(手)')
    amount = db.Column(db.Float, comment='成交额(元)')
    turnover = db.Column(db.Float, comment='换手率(%)')
    change_pct = db.Column(db.Float, comment='涨跌幅(%)')
    
    __table_args__ = (
        db.UniqueConstraint('code', 'trade_date', name='uix_code_date'),
        db.Index('idx_stock_daily_code', 'code'),
        db.Index('idx_stock_daily_date', 'trade_date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'trade_date': self.trade_date.isoformat() if self.trade_date else None,
            'open': self.open,
            'close': self.close,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
            'amount': self.amount,
            'turnover': self.turnover,
            'change_pct': self.change_pct
        }
