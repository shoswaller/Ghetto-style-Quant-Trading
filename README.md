# ⚠️ 免责声明

本系统仅供学习研究使用，不构成任何投资建议。股市有风险，投资需谨慎。

本项目大量使用AI生成，可能存在错误，包括但不限于隐私泄露，数据错误，大量token消耗等，请谨慎使用。

# 丐版量化交易系统

基于 Vue 3 + Flask + 双LLM架构的智能股票分析系统。

## 🎯 功能特性

### MVP版本（个股诊断）
- ✅ 输入股票代码获取实时行情
- ✅ AI智能分析，给出当日/本周/长线操作建议
- ✅ 技术指标计算与展示
- ✅ 两级缓存策略，提升响应速度
- ✅ 支持投资偏好设置

### 待开发功能
- ⏳ 选股筛选
- ⏳ 热门扫描
- ⏳ 操作记录

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────┐
│                 前端 (Vue 3 + Vite)                  │
│           Element Plus • Pinia • Axios              │
└───────────────────────┬─────────────────────────────┘
                        │ REST API
┌───────────────────────▼─────────────────────────────┐
│                   后端 (Flask)                       │
│            SQLAlchemy • AKShare                     │
└──────┬────────────────────────────────────┬─────────┘
       │                                    │
┌──────▼──────┐                    ┌────────▼────────┐
│ 局域网LLM   │                    │    云端LLM      │
│ llama.cpp   │                    │   DeepSeek-V3   │
│ Nemotron-30B│                    │                 │
└─────────────┘                    └─────────────────┘
```

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd Ghetto-style-Quant-Trading
```

### 2. 配置环境变量

云端LLM需要配置API密钥（必需）：

**Windows PowerShell:**
```powershell
$env:CLOUD_API_KEY = "your-api-key-here"
$env:CLOUD_BASE_URL = "https://api.deepseek.com"  # 可选，默认DeepSeek
```

**Linux/Mac:**
```bash
export CLOUD_API_KEY="your-api-key-here"
export CLOUD_BASE_URL="https://api.deepseek.com"
```

### 3. 启动后端

```bash
cd backend

# 激活conda环境
conda activate quanttrading

# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
```

后端将在 `http://127.0.0.1:5000` 启动。

### 4. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:3000` 启动。

## ⚙️ 配置说明

### 云端LLM配置（环境变量）

| 变量名           | 说明         | 默认值                     |
| ---------------- | ------------ | -------------------------- |
| `CLOUD_API_KEY`  | 云端 API密钥 | 必填                       |
| `CLOUD_BASE_URL` | API地址      | `https://api.deepseek.com` |
| `CLOUD_MODEL`    | 模型名称     | `deepseek-chat`            |

> 注：支持任何兼容 OpenAI API 格式的云端模型服务，如 DeepSeek、MiniMax、Kimi 等。

### 局域网LLM配置（配置文件）

编辑 `backend/config/llm_config.json`：

```json
{
    "local_llm": {
        "enabled": true,
        "provider": "llama_cpp",
        "api_url": "http://192.168.1.100:8080",
        "api_key": "",
        "model": "nemotron-30b",
        "timeout": 120
    }
}
```

## 📁 项目结构

```
Ghetto-style-Quant-Trading/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── models/            # 数据库模型
│   │   ├── services/          # 业务服务
│   │   ├── api/               # API路由
│   │   └── utils/             # 工具函数
│   ├── config/
│   │   └── llm_config.json    # 局域网LLM配置
│   └── run.py                 # 启动入口
│
├── frontend/                   # 前端服务
│   ├── src/
│   │   ├── components/        # Vue组件
│   │   ├── views/             # 页面
│   │   ├── api/               # API调用
│   │   └── stores/            # 状态管理
│   └── vite.config.js
│
├── data/                       # SQLite数据库
├── docs/                       # 设计文档
└── README.md
```

## 📖 API接口

| 方法     | 路径                         | 说明         |
| -------- | ---------------------------- | ------------ |
| `GET`    | `/api/health`                | 健康检查     |
| `GET`    | `/api/stock/{code}`          | 获取股票信息 |
| `GET`    | `/api/stock/{code}/daily`    | 获取日线数据 |
| `POST`   | `/api/analysis/diagnose`     | 个股诊断     |
| `DELETE` | `/api/analysis/cache/{code}` | 清除缓存     |

### 个股诊断请求示例

```bash
curl -X POST http://127.0.0.1:5000/api/analysis/diagnose \
  -H "Content-Type: application/json" \
  -d '{"code": "000001", "strategy_preference": "稳健型"}'
```



## 📄 License

MIT License

