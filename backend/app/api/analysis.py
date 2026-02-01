"""
分析相关API
"""
from flask import Blueprint, request, jsonify
from app.services.llm_service import llm_service
from app.services.cache_service import cache_service
from app.models.analysis import UserOperation
from app import db

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/diagnose', methods=['POST'])
def diagnose_stock():
    """
    个股诊断 - 核心接口
    
    POST /api/analysis/diagnose
    {
        "code": "000001",
        "strategy_preference": "稳健型",
        "force_refresh": false
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求体不能为空',
                'data': None
            }), 400
        
        code = data.get('code', '').strip()
        if not code:
            return jsonify({
                'code': 400,
                'message': '股票代码不能为空',
                'data': None
            }), 400
        
        # 标准化股票代码（去除前缀）
        if code.startswith(('sh', 'sz', 'SH', 'SZ')):
            code = code[2:]
        
        strategy_preference = data.get('strategy_preference', '稳健型')
        force_refresh = data.get('force_refresh', False)
        
        # 调用LLM服务进行诊断
        result = llm_service.diagnose_stock(
            code=code,
            strategy_preference=strategy_preference,
            force_refresh=force_refresh
        )
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result
        })
    
    except ValueError as e:
        return jsonify({
            'code': 400,
            'message': str(e),
            'data': None
        }), 400
    
    except RuntimeError as e:
        return jsonify({
            'code': 503,
            'message': str(e),
            'data': None
        }), 503
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'诊断失败: {str(e)}',
            'data': None
        }), 500


@analysis_bp.route('/cache/<code>', methods=['GET'])
def get_cache(code: str):
    """
    获取缓存的分析结果
    
    GET /api/analysis/cache/000001
    """
    try:
        from app.models.analysis import AnalysisCache
        
        caches = AnalysisCache.query.filter_by(code=code).all()
        if not caches:
            return jsonify({
                'code': 404,
                'message': f'未找到股票 {code} 的缓存',
                'data': None
            }), 404
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'code': code,
                'caches': [c.to_dict() for c in caches]
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取缓存失败: {str(e)}',
            'data': None
        }), 500


@analysis_bp.route('/cache/<code>', methods=['DELETE'])
def clear_cache(code: str):
    """
    清除缓存
    
    DELETE /api/analysis/cache/000001
    """
    try:
        cache_service.invalidate(code)
        
        return jsonify({
            'code': 200,
            'message': f'已清除股票 {code} 的缓存',
            'data': None
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'清除缓存失败: {str(e)}',
            'data': None
        }), 500


@analysis_bp.route('/operation', methods=['POST'])
def record_operation():
    """
    记录用户操作
    
    POST /api/analysis/operation
    {
        "code": "000001",
        "operation_type": "buy",
        "price": 12.35,
        "quantity": 1000,
        "notes": "分批建仓"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求体不能为空',
                'data': None
            }), 400
        
        code = data.get('code', '').strip()
        operation_type = data.get('operation_type', '').strip()
        
        if not code or not operation_type:
            return jsonify({
                'code': 400,
                'message': '股票代码和操作类型不能为空',
                'data': None
            }), 400
        
        if operation_type not in ['buy', 'sell', 'watch']:
            return jsonify({
                'code': 400,
                'message': '操作类型必须是 buy/sell/watch',
                'data': None
            }), 400
        
        operation = UserOperation(
            code=code,
            operation_type=operation_type,
            price=data.get('price'),
            quantity=data.get('quantity'),
            notes=data.get('notes', '')
        )
        
        db.session.add(operation)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '操作记录成功',
            'data': operation.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'记录操作失败: {str(e)}',
            'data': None
        }), 500


@analysis_bp.route('/operation/history', methods=['GET'])
def get_operation_history():
    """
    获取操作历史
    
    GET /api/analysis/operation/history?code=000001&limit=50
    """
    try:
        code = request.args.get('code', '')
        limit = request.args.get('limit', 50, type=int)
        limit = min(max(limit, 1), 200)  # 限制范围1-200
        
        query = UserOperation.query
        if code:
            query = query.filter_by(code=code)
        
        operations = query.order_by(UserOperation.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total': len(operations),
                'operations': [op.to_dict() for op in operations]
            }
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取操作历史失败: {str(e)}',
            'data': None
        }), 500
