"""
丐版量化交易系统 - 启动入口
"""
import os
from app import create_app

# 确定运行环境
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    print("=" * 50)
    print("丐版量化交易系统")
    print("=" * 50)
    print(f"运行环境: {env}")
    print(f"API地址: http://127.0.0.1:5000")
    print("=" * 50)
    
    # 检查LLM配置
    from app.services.cloud_llm import cloud_llm
    from app.services.local_llm import local_llm
    
    if cloud_llm.enabled:
        print("✓ 云端LLM 已配置")
    else:
        print("✗ 云端LLM 未配置 (请设置 CLOUD_API_KEY 环境变量)")
    
    if local_llm.enabled:
        print(f"✓ 局域网LLM 已配置 ({local_llm.api_url})")
    else:
        print("✗ 局域网LLM 未启用 (可选)")
    
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=(env == 'development'))
