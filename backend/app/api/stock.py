"""
股票相关API
"""
from flask import Blueprint, request, jsonify
from app.services.data_service import data_service
from app.models.stock import Stock, StockDaily
from app import db

stock_bp = Blueprint('stock', __name__)


@stock_bp.route('/<code>', methods=['GET'])
def get_stock_info(code: str):
    """
    获取股票基本信息
    
    GET /api/stock/000001
    """
    try:
        info = data_service.get_stock_info(code)
        if not info:
            return jsonify({
                'code': 404,
                'message': f'未找到股票 {code}',
                'data': None
            }), 404
        
        # 获取实时行情
        realtime = data_service.get_realtime_quote(code)
        if realtime:
            info['current_price'] = realtime['current_price']
            info['change_pct'] = realtime['change_pct']
            info['volume'] = realtime['volume']
            info['amount'] = realtime['amount']
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': info
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取股票信息失败: {str(e)}',
            'data': None
        }), 500


@stock_bp.route('/<code>/daily', methods=['GET'])
def get_stock_daily(code: str):
    """
    获取股票日线数据
    
    GET /api/stock/000001/daily?days=60
    """
    try:
        days = request.args.get('days', 60, type=int)
        days = min(max(days, 1), 250)  # 限制范围1-250
        
        daily_data = data_service.get_daily_data(code, days)
        if not daily_data:
            return jsonify({
                'code': 404,
                'message': f'未找到股票 {code} 的日线数据',
                'data': None
            }), 404
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'code': code,
                'days': len(daily_data),
                'daily': daily_data
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取日线数据失败: {str(e)}',
            'data': None
        }), 500


@stock_bp.route('/<code>/technical', methods=['GET'])
def get_technical_indicators(code: str):
    """
    获取股票技术指标
    
    GET /api/stock/000001/technical
    """
    try:
        indicators = data_service.get_technical_indicators(code)
        if not indicators:
            return jsonify({
                'code': 404,
                'message': f'无法计算股票 {code} 的技术指标',
                'data': None
            }), 404
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'code': code,
                'indicators': indicators
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取技术指标失败: {str(e)}',
            'data': None
        }), 500


@stock_bp.route('/<code>/fund-flow', methods=['GET'])
def get_fund_flow(code: str):
    """
    获取资金流向
    
    GET /api/stock/000001/fund-flow
    """
    try:
        fund_flow = data_service.get_fund_flow(code)
        if not fund_flow:
            return jsonify({
                'code': 404,
                'message': f'无法获取股票 {code} 的资金流向',
                'data': None
            }), 404
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'code': code,
                'fund_flow': fund_flow
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取资金流向失败: {str(e)}',
            'data': None
        }), 500
