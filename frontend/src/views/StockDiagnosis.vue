<template>
  <div class="diagnosis-page">
    <!-- 搜索区域 -->
    <section class="search-section glass-card">
      <h2 class="section-title">
        <el-icon><DataAnalysis /></el-icon>
        个股诊断
      </h2>
      
      <div class="search-form">
        <div class="input-group">
          <el-input
            v-model="stockCode"
            placeholder="请输入股票代码，如 000001"
            size="large"
            :prefix-icon="Search"
            @keyup.enter="handleDiagnose"
            clearable
          />
          <el-button 
            type="primary" 
            size="large" 
            :loading="stockStore.isLoading"
            @click="handleDiagnose"
          >
            {{ stockStore.isLoading ? '分析中...' : '诊断' }}
          </el-button>
        </div>
        
        <div class="strategy-options">
          <span class="label">投资偏好：</span>
          <el-radio-group v-model="stockStore.strategyPreference" size="default">
            <el-radio-button label="稳健型">稳健型</el-radio-button>
            <el-radio-button label="激进型">激进型</el-radio-button>
            <el-radio-button label="价值型">价值型</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      
      <!-- 历史记录 -->
      <div v-if="stockStore.searchHistory.length > 0" class="history-section">
        <span class="label">最近查询：</span>
        <div class="history-tags">
          <el-tag 
            v-for="item in stockStore.searchHistory.slice(0, 5)" 
            :key="item.code"
            class="history-tag"
            @click="quickSearch(item.code)"
          >
            {{ item.name }} ({{ item.code }})
          </el-tag>
        </div>
      </div>
    </section>
    
    <!-- 加载状态 -->
    <section v-if="stockStore.isLoading" class="loading-section">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p class="loading-text">正在分析股票数据，请稍候...</p>
        <p class="loading-hint">AI分析可能需要30-60秒</p>
      </div>
    </section>
    
    <!-- 错误提示 -->
    <section v-else-if="stockStore.error" class="error-section glass-card">
      <el-icon :size="48" color="#f56c6c"><CircleCloseFilled /></el-icon>
      <h3>分析失败</h3>
      <p>{{ stockStore.error }}</p>
      <el-button type="primary" @click="stockStore.clearResult">重试</el-button>
    </section>
    
    <!-- 分析结果 -->
    <section v-else-if="stockStore.hasResult" class="result-section fade-in">
      <!-- 股票信息卡片 -->
      <div class="stock-info-card glass-card">
        <div class="stock-header">
          <div class="stock-name-group">
            <h2 class="stock-name">{{ stockStore.currentStock.name }}</h2>
            <span class="stock-code">{{ stockStore.currentStock.code }}</span>
            <el-tag size="small" type="info">{{ stockStore.currentStock.industry }}</el-tag>
          </div>
          <div class="stock-price-group">
            <span class="current-price" :class="stockStore.priceChangeClass">
              ¥{{ stockStore.currentStock.current_price?.toFixed(2) || 'N/A' }}
            </span>
            <span class="price-change" :class="stockStore.priceChangeClass">
              {{ stockStore.currentStock.change_pct > 0 ? '+' : '' }}{{ stockStore.currentStock.change_pct?.toFixed(2) || 0 }}%
            </span>
          </div>
        </div>
        
        <div class="stock-actions">
          <el-button :icon="Refresh" @click="handleRefresh">刷新分析</el-button>
          <el-button :icon="Document" @click="showRecordDialog = true">记录操作</el-button>
        </div>
      </div>
      
      <!-- 操作建议卡片 -->
      <div class="suggestions-grid">
        <AnalysisCard 
          title="当日建议"
          icon="📅"
          :data="stockStore.analysisResult.daily"
          timeframe="短线"
        />
        <AnalysisCard 
          title="本周建议"
          icon="📆"
          :data="stockStore.analysisResult.weekly"
          timeframe="波段"
        />
        <AnalysisCard 
          title="长线建议"
          icon="📈"
          :data="stockStore.analysisResult.longterm"
          timeframe="1-3月"
        />
      </div>
      
      <!-- 综合分析 -->
      <div class="analysis-detail glass-card">
        <h3>
          <el-icon><Document /></el-icon>
          综合分析
        </h3>
        <p class="analysis-summary">{{ stockStore.analysisResult.summary }}</p>
      </div>
      
      <!-- 技术指标 -->
      <div class="technical-section glass-card">
        <h3>
          <el-icon><DataLine /></el-icon>
          技术指标
        </h3>
        <div class="indicators-grid">
          <div class="indicator-item">
            <span class="indicator-label">MA5</span>
            <span class="indicator-value">{{ stockStore.analysisResult.technical_indicators?.ma5 || 'N/A' }}</span>
          </div>
          <div class="indicator-item">
            <span class="indicator-label">MA10</span>
            <span class="indicator-value">{{ stockStore.analysisResult.technical_indicators?.ma10 || 'N/A' }}</span>
          </div>
          <div class="indicator-item">
            <span class="indicator-label">MA20</span>
            <span class="indicator-value">{{ stockStore.analysisResult.technical_indicators?.ma20 || 'N/A' }}</span>
          </div>
          <div class="indicator-item">
            <span class="indicator-label">MACD</span>
            <span class="indicator-value" :class="getMacdClass">
              {{ stockStore.analysisResult.technical_indicators?.macd?.signal || 'N/A' }}
            </span>
          </div>
          <div class="indicator-item">
            <span class="indicator-label">KDJ</span>
            <span class="indicator-value">
              {{ stockStore.analysisResult.technical_indicators?.kdj?.signal || 'N/A' }}
            </span>
          </div>
          <div class="indicator-item">
            <span class="indicator-label">RSI</span>
            <span class="indicator-value">{{ stockStore.analysisResult.technical_indicators?.rsi || 'N/A' }}</span>
          </div>
        </div>
      </div>
    </section>
    
    <!-- 空状态 -->
    <section v-else class="empty-section">
      <div class="empty-content">
        <el-icon :size="64" color="#6e7681"><Search /></el-icon>
        <h3>输入股票代码开始诊断</h3>
        <p>系统将综合分析技术面和基本面，给出操作建议</p>
      </div>
    </section>
    
    <!-- 记录操作弹窗 -->
    <el-dialog v-model="showRecordDialog" title="记录操作" width="400px">
      <el-form :model="operationForm" label-width="80px">
        <el-form-item label="操作类型">
          <el-radio-group v-model="operationForm.operation_type">
            <el-radio-button label="buy">买入</el-radio-button>
            <el-radio-button label="sell">卖出</el-radio-button>
            <el-radio-button label="watch">观望</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="operationForm.price" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="operationForm.quantity" :min="0" :step="100" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="operationForm.notes" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRecordDialog = false">取消</el-button>
        <el-button type="primary" @click="handleRecordOperation">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Search, DataAnalysis, Refresh, Document, 
  CircleCloseFilled, DataLine 
} from '@element-plus/icons-vue'
import { useStockStore } from '@/stores/stock'
import { recordOperation } from '@/api/stock'
import AnalysisCard from '@/components/AnalysisCard.vue'

const stockStore = useStockStore()
const stockCode = ref('')
const showRecordDialog = ref(false)

const operationForm = reactive({
  operation_type: 'buy',
  price: 0,
  quantity: 0,
  notes: ''
})

const getMacdClass = computed(() => {
  const signal = stockStore.analysisResult?.technical_indicators?.macd?.signal
  if (signal === '金叉') return 'price-up'
  if (signal === '死叉') return 'price-down'
  return ''
})

const handleDiagnose = async () => {
  if (!stockCode.value.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  try {
    await stockStore.diagnose(stockCode.value.trim())
    ElMessage.success('分析完成')
  } catch (e) {
    ElMessage.error(stockStore.error || '分析失败')
  }
}

const handleRefresh = async () => {
  if (!stockStore.currentStock?.code) return
  
  try {
    await stockStore.diagnose(stockStore.currentStock.code, true)
    ElMessage.success('刷新成功')
  } catch (e) {
    ElMessage.error(stockStore.error || '刷新失败')
  }
}

const quickSearch = (code) => {
  stockCode.value = code
  handleDiagnose()
}

const handleRecordOperation = async () => {
  if (!stockStore.currentStock?.code) return
  
  try {
    await recordOperation({
      code: stockStore.currentStock.code,
      ...operationForm
    })
    ElMessage.success('记录成功')
    showRecordDialog.value = false
  } catch (e) {
    ElMessage.error('记录失败')
  }
}
</script>

<style scoped>
.diagnosis-page {
  max-width: 1000px;
  margin: 0 auto;
}

/* 搜索区域 */
.search-section {
  padding: 32px;
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.25rem;
  margin-bottom: 24px;
}

.search-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  display: flex;
  gap: 12px;
}

.input-group .el-input {
  flex: 1;
}

.strategy-options {
  display: flex;
  align-items: center;
  gap: 12px;
}

.strategy-options .label,
.history-section .label {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.history-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.history-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.history-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.history-tag:hover {
  transform: scale(1.05);
}

/* 加载状态 */
.loading-section {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}

.loading-content {
  text-align: center;
}

.loading-text {
  margin-top: 24px;
  font-size: 1.125rem;
}

.loading-hint {
  margin-top: 8px;
  color: var(--text-muted);
  font-size: 0.875rem;
}

/* 错误状态 */
.error-section {
  padding: 48px;
  text-align: center;
}

.error-section h3 {
  margin: 16px 0 8px;
}

.error-section p {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

/* 股票信息卡片 */
.stock-info-card {
  padding: 24px;
  margin-bottom: 24px;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.stock-name-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stock-name {
  font-size: 1.5rem;
  font-weight: 600;
}

.stock-code {
  color: var(--text-muted);
}

.stock-price-group {
  text-align: right;
}

.current-price {
  display: block;
  font-size: 2rem;
  font-weight: 600;
}

.price-change {
  font-size: 1.125rem;
}

.stock-actions {
  display: flex;
  gap: 12px;
}

/* 建议卡片网格 */
.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

/* 综合分析 */
.analysis-detail {
  padding: 24px;
  margin-bottom: 24px;
}

.analysis-detail h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.analysis-summary {
  color: var(--text-secondary);
  line-height: 1.8;
}

/* 技术指标 */
.technical-section {
  padding: 24px;
}

.technical-section h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.indicators-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.indicator-item {
  text-align: center;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.indicator-label {
  display: block;
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-bottom: 8px;
}

.indicator-value {
  font-size: 1rem;
  font-weight: 500;
}

/* 空状态 */
.empty-section {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}

.empty-content {
  text-align: center;
}

.empty-content h3 {
  margin: 24px 0 8px;
  color: var(--text-secondary);
}

.empty-content p {
  color: var(--text-muted);
}

/* 响应式 */
@media (max-width: 768px) {
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
  
  .indicators-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .stock-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .stock-price-group {
    text-align: left;
  }
}
</style>
