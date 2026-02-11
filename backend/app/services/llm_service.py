"""
LLM服务 - 整合局域网LLM和云端LLM
"""
import json
import logging
from typing import Dict, Optional
from app.services.local_llm import local_llm
from app.services.cloud_llm import cloud_llm
from app.services.data_service import data_service
from app.services.cache_service import cache_service
from app.utils.prompts import (
    DATA_STRUCTURE_PROMPT,
    STOCK_ANALYSIS_PROMPT,
    SYSTEM_PROMPT
)

logger = logging.getLogger(__name__)

class LLMService:
    """LLM服务 - 协调端侧和云端LLM"""
    
    def __init__(self):
        self.local_llm = local_llm
        self.cloud_llm = cloud_llm
        self.data_service = data_service
        self.cache_service = cache_service
    
    def diagnose_stock(self, code: str, user_preference: str = "",
                       force_refresh: bool = False) -> Dict:
        """
        个股诊断 - 核心功能
        
        Args:
            code: 股票代码
            user_preference: 用户投资偏好描述（可选，由LLM自主分析）
            force_refresh: 是否强制刷新缓存
            
        Returns:
            诊断结果
        """
        # 1. 获取股票基本信息和实时行情
        stock_info = self.data_service.get_stock_info(code)
        if not stock_info:
            raise ValueError(f"无法获取股票 {code} 的信息，请检查股票代码是否正确")
        
        realtime = self.data_service.get_realtime_quote(code)
        if realtime:
            stock_info['current_price'] = realtime['current_price']
            stock_info['change_pct'] = realtime['change_pct']
        
        # 2. 获取日线数据
        daily_data = self.data_service.get_daily_data(code, 60)
        if not daily_data:
            raise ValueError(f"无法获取股票 {code} 的历史数据")
        
        # 3. 计算数据指纹
        latest = daily_data[-1]
        data_hash = self.cache_service.make_data_hash(
            latest['close'], 
            latest['volume'], 
            latest['trade_date']
        )
        
        # 4. 检查缓存（除非强制刷新）
        if not force_refresh:
            cached_result = self._get_cached_analysis(code, data_hash)
            if cached_result:
                return {
                    'stock_info': stock_info,
                    'analysis': cached_result,
                    'cached': True,
                    'generated_at': None  # 来自缓存
                }
        
        # 5. 获取技术指标
        technical = self.data_service.get_technical_indicators(code)
        
        # 6. 获取资金流向（可选）
        fund_flow = self.data_service.get_fund_flow(code)
        
        # 7. 调用LLM进行分析
        analysis_result = self._analyze_with_llm(
            stock_info=stock_info,
            daily_data=daily_data[-20:],  # 只取最近20天
            technical=technical,
            fund_flow=fund_flow,
            user_preference=user_preference
        )
        
        # 8. 合并技术指标到结果
        analysis_result['technical_indicators'] = technical
        
        # 9. 缓存结果
        self._cache_analysis(code, data_hash, analysis_result)
        
        from datetime import datetime
        return {
            'stock_info': stock_info,
            'analysis': analysis_result,
            'cached': False,
            'generated_at': datetime.now().isoformat()
        }
    
    def _analyze_with_llm(self, stock_info: Dict, daily_data: list,
                          technical: Dict, fund_flow: Optional[Dict],
                          user_preference: str) -> Dict:
        """
        使用云端LLM进行分析
        
        流程：
        1. 准备数据摘要
        2. 直接使用云端LLM进行分析（LLM自主给出策略）
        """
        # 检查云端LLM是否可用
        if not self.cloud_llm.enabled:
            raise RuntimeError("未配置云端LLM，无法进行分析")
        
        # 准备数据摘要
        data_summary = self._prepare_data_summary(
            stock_info, daily_data, technical, fund_flow
        )
        
        # 使用云端LLM进行分析
        analysis_prompt = STOCK_ANALYSIS_PROMPT.format(
            stock_name=stock_info.get('name', ''),
            stock_code=stock_info.get('code', ''),
            structured_data=data_summary,
            user_preference=user_preference if user_preference else "无特殊偏好，请自主分析并给出完整策略建议"
        )
        
        try:
            response = self.cloud_llm.complete(
                analysis_prompt, 
                system_prompt=SYSTEM_PROMPT
            )
            
            # 解析JSON响应
            return self._parse_analysis_response(response)
        except Exception as e:
            raise RuntimeError(f"云端LLM分析失败: {e}")
    
    def _prepare_data_summary(self, stock_info: Dict, daily_data: list,
                              technical: Dict, fund_flow: Optional[Dict]) -> str:
        """准备数据摘要"""
        summary = f"""
## 股票基本信息
- 股票名称: {stock_info.get('name', 'N/A')}
- 股票代码: {stock_info.get('code', 'N/A')}
- 所属行业: {stock_info.get('industry', 'N/A')}
- 市盈率: {stock_info.get('pe_ratio', 'N/A')}
- 市净率: {stock_info.get('pb_ratio', 'N/A')}
- 当前价格: {stock_info.get('current_price', 'N/A')}
- 涨跌幅: {stock_info.get('change_pct', 'N/A')}%

## 近期走势（最近5日）
"""
        # 添加最近5天的数据
        for day in daily_data[-5:]:
            summary += f"- {day['trade_date']}: 开{day['open']} 收{day['close']} 高{day['high']} 低{day['low']} 涨跌{day['change_pct']}%\n"
        
        # 添加技术指标
        if technical:
            summary += f"""
## 技术指标
- MA5: {technical.get('ma5', 'N/A')}
- MA10: {technical.get('ma10', 'N/A')}
- MA20: {technical.get('ma20', 'N/A')}
- MACD: {technical.get('macd', {}).get('signal', 'N/A')}
- KDJ: K={technical.get('kdj', {}).get('k', 'N/A')}, D={technical.get('kdj', {}).get('d', 'N/A')}, J={technical.get('kdj', {}).get('j', 'N/A')}
- RSI: {technical.get('rsi', 'N/A')}
"""
        
        # 添加资金流向
        if fund_flow:
            summary += f"""
## 资金流向
- 主力净流入: {fund_flow.get('main_net_inflow', 'N/A')}
- 主力净流入占比: {fund_flow.get('main_net_inflow_pct', 'N/A')}%
"""
        
        return summary
    
    def _parse_analysis_response(self, response: str) -> Dict:
        """解析LLM的分析响应"""
        try:
            # 尝试提取JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # 如果无法解析JSON，返回文本格式
        return {
            'summary': response,
            'daily': {
                'trend': '无法解析',
                'suggestion': '请查看综合分析',
                'confidence': 0.5,
                'reason': response[:200]
            },
            'weekly': {
                'trend': '无法解析',
                'suggestion': '请查看综合分析',
                'confidence': 0.5,
                'reason': ''
            },
            'longterm': {
                'trend': '无法解析',
                'suggestion': '请查看综合分析',
                'confidence': 0.5,
                'reason': ''
            }
        }
    
    def _get_cached_analysis(self, code: str, data_hash: str) -> Optional[Dict]:
        """获取缓存的分析结果"""
        # 简化缓存：只使用一个键
        cached = self.cache_service.get(code, 'analysis', data_hash)
        return cached
    
    def _cache_analysis(self, code: str, data_hash: str, result: Dict):
        """缓存分析结果"""
        # 简化缓存：只存储一次
        self.cache_service.set(code, 'analysis', data_hash, result)


# 单例
llm_service = LLMService()
