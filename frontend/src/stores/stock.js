import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { diagnoseStock, getStockInfo } from '@/api/stock'

export const useStockStore = defineStore('stock', () => {
    // 状态
    const currentStock = ref(null)
    const analysisResult = ref(null)
    const isLoading = ref(false)
    const error = ref(null)

    // 用户投资偏好描述（可选，由LLM自主分析）- 从localStorage恢复
    const userPreference = ref(localStorage.getItem('userPreference') || '')

    // 历史查询记录 - 从localStorage恢复
    const savedHistory = localStorage.getItem('searchHistory')
    const searchHistory = ref(savedHistory ? JSON.parse(savedHistory) : [])

    // 持久化到localStorage
    watch(userPreference, (newVal) => {
        localStorage.setItem('userPreference', newVal)
    })

    watch(searchHistory, (newVal) => {
        localStorage.setItem('searchHistory', JSON.stringify(newVal))
    }, { deep: true })

    // 计算属性
    const hasResult = computed(() => !!analysisResult.value)

    const priceChangeClass = computed(() => {
        if (!currentStock.value?.change_pct) return 'price-flat'
        return currentStock.value.change_pct > 0 ? 'price-up' :
            currentStock.value.change_pct < 0 ? 'price-down' : 'price-flat'
    })

    // 方法
    const diagnose = async (code, forceRefresh = false) => {
        isLoading.value = true
        error.value = null

        try {
            const response = await diagnoseStock(code, userPreference.value, forceRefresh)

            if (response.code === 200) {
                currentStock.value = response.data.stock_info
                analysisResult.value = response.data.analysis

                // 添加到历史记录
                addToHistory(code, response.data.stock_info.name)

                return response.data
            } else {
                throw new Error(response.message)
            }
        } catch (e) {
            error.value = e.response?.data?.message || e.message || '诊断失败'
            throw e
        } finally {
            isLoading.value = false
        }
    }

    const addToHistory = (code, name) => {
        // 移除重复项
        const index = searchHistory.value.findIndex(item => item.code === code)
        if (index > -1) {
            searchHistory.value.splice(index, 1)
        }

        // 添加到开头
        searchHistory.value.unshift({ code, name, time: new Date().toISOString() })

        // 保留最近10条
        if (searchHistory.value.length > 10) {
            searchHistory.value.pop()
        }
    }

    const clearResult = () => {
        currentStock.value = null
        analysisResult.value = null
        error.value = null
    }

    const setUserPreference = (preference) => {
        userPreference.value = preference
    }

    return {
        // 状态
        currentStock,
        analysisResult,
        isLoading,
        error,
        userPreference,
        searchHistory,

        // 计算属性
        hasResult,
        priceChangeClass,

        // 方法
        diagnose,
        clearResult,
        setUserPreference
    }
})
