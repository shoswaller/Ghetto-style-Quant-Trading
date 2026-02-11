import axios from 'axios'

// 创建axios实例
const api = axios.create({
    baseURL: '/api',
    timeout: 120000  // 2分钟超时，因为LLM分析可能较慢
})

// 健康检查
export const checkHealth = async () => {
    const response = await api.get('/health')
    return response.data
}

// 获取股票信息
export const getStockInfo = async (code) => {
    const response = await api.get(`/stock/${code}`)
    return response.data
}

// 获取日线数据
export const getStockDaily = async (code, days = 60) => {
    const response = await api.get(`/stock/${code}/daily`, { params: { days } })
    return response.data
}

// 获取技术指标
export const getTechnicalIndicators = async (code) => {
    const response = await api.get(`/stock/${code}/technical`)
    return response.data
}

// 个股诊断
export const diagnoseStock = async (code, userPreference = '', forceRefresh = false) => {
    const response = await api.post('/analysis/diagnose', {
        code,
        user_preference: userPreference,
        force_refresh: forceRefresh
    })
    return response.data
}

// 清除缓存
export const clearCache = async (code) => {
    const response = await api.delete(`/analysis/cache/${code}`)
    return response.data
}

// 记录操作
export const recordOperation = async (data) => {
    const response = await api.post('/analysis/operation', data)
    return response.data
}

// 获取操作历史
export const getOperationHistory = async (code = '', limit = 50) => {
    const response = await api.get('/analysis/operation/history', {
        params: { code, limit }
    })
    return response.data
}

export default api
