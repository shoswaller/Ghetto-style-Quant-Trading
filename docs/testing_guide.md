# 丐版量化交易系统 - 启动与测试指南

## 1. 环境准备

### 1.1 创建Conda环境

```powershell
# 创建conda环境
conda create -n quanttrading python=3.11 -y

# 激活环境
conda activate quanttrading
```

### 1.2 配置云端LLM环境变量

在启动后端之前，需要配置云端LLM的API密钥：

```powershell
# Windows PowerShell（临时生效，仅当前会话）
$env:CLOUD_API_KEY = "your-api-key-here"
$env:CLOUD_BASE_URL = "https://api.deepseek.com"  # 可选，默认DeepSeek

# 如需永久生效，可添加到系统环境变量：
# 1. 右键"此电脑" -> 属性 -> 高级系统设置 -> 环境变量
# 2. 在"用户变量"中新建 CLOUD_API_KEY 和 CLOUD_BASE_URL
```

**支持的云端模型服务：**

| 服务商   | CLOUD_BASE_URL             | 模型示例         |
| -------- | -------------------------- | ---------------- |
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat`  |
| MiniMax  | `https://api.minimax.chat` | `abab6.5-chat`   |
| Kimi     | `https://api.moonshot.cn`  | `moonshot-v1-8k` |
| OpenAI   | `https://api.openai.com`   | `gpt-4`          |

---

## 2. 启动后端

### 2.1 安装依赖

```powershell
cd e:\project\Ghetto-style-Quant-Trading\backend

# 确保已激活conda环境
conda activate quanttrading

# 安装Python依赖
pip install -r requirements.txt
```

**常见问题：**
- 如果 `akshare` 安装失败，尝试：`pip install akshare --upgrade`
- 如果 `httpx` 版本冲突，尝试：`pip install httpx==0.26.0`

### 2.2 启动Flask服务

```powershell
cd e:\project\Ghetto-style-Quant-Trading\backend

# 设置环境变量（如果还没设置）
$env:CLOUD_API_KEY = "your-api-key"

# 启动服务
python run.py
```

**预期输出：**
```
==================================================
丐版量化交易系统
==================================================
运行环境: development
API地址: http://127.0.0.1:5000
==================================================
✓ 云端LLM 已配置
✗ 局域网LLM 未启用 (可选)
==================================================
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

---

## 3. 启动前端

### 3.1 安装Node.js依赖

```powershell
cd e:\project\Ghetto-style-Quant-Trading\frontend

# 安装依赖
npm install
```

**Node.js版本要求：** >= 18.0.0

### 3.2 启动开发服务器

```powershell
npm run dev
```

**预期输出：**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## 4. 功能测试

### 4.1 健康检查

**测试后端是否正常运行：**

```powershell
# PowerShell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/health"
```

**预期响应：**
```json
{
    "status": "ok",
    "message": "丐版量化交易系统运行中"
}
```

### 4.2 获取股票信息

**测试AKShare数据获取：**

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/stock/000001"
```

**预期响应：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "code": "000001",
        "name": "平安银行",
        "industry": "银行",
        "current_price": 12.35,
        "change_pct": 1.23
    }
}
```

### 4.3 获取日线数据

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/stock/000001/daily?days=5"
```

### 4.4 获取技术指标

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/stock/000001/technical"
```

### 4.5 个股诊断（核心功能）

**⚠️ 注意：此接口会调用云端LLM，可能需要30-60秒，并消耗API token**

```powershell
# PowerShell
$body = @{
    code = "000001"
    strategy_preference = "稳健型"
    force_refresh = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/analysis/diagnose" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**或使用curl（Git Bash / WSL）：**

```bash
curl -X POST http://127.0.0.1:5000/api/analysis/diagnose \
  -H "Content-Type: application/json" \
  -d '{"code": "000001", "strategy_preference": "稳健型", "force_refresh": false}'
```

**预期响应：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "stock_info": {
            "code": "000001",
            "name": "平安银行",
            "industry": "银行",
            "current_price": 12.35,
            "change_pct": 1.23
        },
        "analysis": {
            "summary": "平安银行当前处于震荡整理阶段...",
            "daily": {
                "trend": "震荡",
                "suggestion": "观望",
                "confidence": 0.75,
                "reason": "..."
            },
            "weekly": { ... },
            "longterm": { ... },
            "technical_indicators": { ... }
        },
        "cached": false,
        "generated_at": "2026-02-01T10:30:00"
    }
}
```

### 4.6 清除缓存

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/analysis/cache/000001" -Method DELETE
```

---

## 5. 前端页面测试

1. 打开浏览器访问 `http://localhost:3000`
2. 点击导航栏的"个股诊断"
3. 在输入框输入股票代码，如 `000001`
4. 选择投资偏好（稳健型/激进型/价值型）
5. 点击"诊断"按钮
6. 等待分析结果（30-60秒）

**测试检查点：**
- [ ] 首页正常显示
- [ ] 导航栏正常切换
- [ ] 股票代码输入正常
- [ ] 投资偏好选择正常
- [ ] 加载动画显示
- [ ] 分析结果正确展示
- [ ] 技术指标正确显示
- [ ] 刷新分析功能正常
- [ ] 记录操作功能正常

---

## 6. 局域网LLM配置（可选）

如果您有局域网部署的LLM（通过llama.cpp），可以编辑配置文件启用：

**编辑 `backend/config/llm_config.json`：**

```json
{
    "local_llm": {
        "enabled": true,
        "provider": "llama_cpp",
        "api_url": "http://192.168.1.100:8080",  // 改为您的llama.cpp服务地址
        "api_key": "",
        "model": "nemotron-30b",
        "timeout": 120,
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "fallback": {
        "enabled": true,
        "use_cloud_on_local_failure": true
    }
}
```

**验证局域网LLM连接：**

```powershell
# 测试llama.cpp server是否可访问
Invoke-RestMethod -Uri "http://192.168.1.100:8080/health"
```

---

## 7. 常见问题排查

### 7.1 后端启动失败

**问题：** `ModuleNotFoundError: No module named 'xxx'`

**解决：**
```powershell
conda activate quanttrading
pip install -r requirements.txt
```

### 7.2 AKShare数据获取失败

**问题：** `获取股票信息失败: xxx`

**可能原因：**
- 网络连接问题
- AKShare接口变更
- 股票代码格式错误

**解决：**
```powershell
# 测试AKShare是否正常
python -c "import akshare as ak; print(ak.stock_zh_a_spot_em().head())"
```

### 7.3 云端LLM调用失败

**问题：** `未配置 CLOUD_API_KEY 环境变量`

**解决：**
```powershell
# 检查环境变量是否设置
echo $env:CLOUD_API_KEY

# 如果为空，重新设置
$env:CLOUD_API_KEY = "your-api-key"
```

**问题：** `云端LLM请求超时`

**可能原因：**
- 网络问题
- API服务拥堵
- 请求内容过长

### 7.4 前端无法连接后端

**问题：** 前端显示网络错误

**解决：**
1. 确认后端已启动（`http://127.0.0.1:5000/api/health`）
2. 检查 `frontend/vite.config.js` 中的代理配置
3. 检查是否有CORS问题

### 7.5 数据库错误

**问题：** `sqlalchemy.exc.OperationalError`

**解决：**
```powershell
# 删除旧数据库文件，重新创建
Remove-Item e:\project\Ghetto-style-Quant-Trading\data\quant.db -ErrorAction SilentlyContinue
python run.py  # 重启后端会自动创建新数据库
```

---

## 8. 测试用股票代码

| 代码   | 名称     | 说明             |
| ------ | -------- | ---------------- |
| 000001 | 平安银行 | 银行股，适合测试 |
| 600519 | 贵州茅台 | 白酒龙头         |
| 000858 | 五粮液   | 白酒股           |
| 002594 | 比亚迪   | 新能源汽车       |
| 600036 | 招商银行 | 银行股           |
| 000002 | 万科A    | 房地产           |

---

## 9. 关闭服务

```powershell
# 关闭后端：在运行 run.py 的终端按 Ctrl+C
# 关闭前端：在运行 npm run dev 的终端按 Ctrl+C

# 退出conda环境
conda deactivate
```
