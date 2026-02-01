<template>
  <div class="analysis-card glass-card" :class="suggestionClass">
    <div class="card-header">
      <span class="card-icon">{{ icon }}</span>
      <div class="card-title-group">
        <h4 class="card-title">{{ title }}</h4>
        <span class="card-timeframe">{{ timeframe }}</span>
      </div>
    </div>
    
    <div class="card-body">
      <div class="trend-row">
        <span class="label">趋势</span>
        <span class="value">{{ data?.trend || 'N/A' }}</span>
      </div>
      
      <div class="suggestion-row">
        <span class="suggestion-badge" :class="suggestionBadgeClass">
          {{ data?.suggestion || 'N/A' }}
        </span>
      </div>
      
      <div class="confidence-row">
        <span class="label">置信度</span>
        <div class="confidence-bar">
          <div 
            class="confidence-fill" 
            :style="{ width: confidencePercent + '%' }"
          ></div>
        </div>
        <span class="confidence-value">{{ confidencePercent }}%</span>
      </div>
    </div>
    
    <div class="card-footer">
      <p class="reason">{{ data?.reason || '暂无分析理由' }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  icon: { type: String, default: '📊' },
  data: { type: Object, default: () => ({}) },
  timeframe: { type: String, default: '' }
})

const confidencePercent = computed(() => {
  const conf = props.data?.confidence
  if (typeof conf === 'number') {
    return Math.round(conf * 100)
  }
  return 50
})

const suggestionClass = computed(() => {
  const suggestion = props.data?.suggestion?.toLowerCase()
  if (!suggestion) return ''
  
  if (suggestion.includes('买') || suggestion.includes('加')) return 'suggestion-buy'
  if (suggestion.includes('卖') || suggestion.includes('减')) return 'suggestion-sell'
  return 'suggestion-hold'
})

const suggestionBadgeClass = computed(() => {
  const suggestion = props.data?.suggestion?.toLowerCase()
  if (!suggestion) return ''
  
  if (suggestion.includes('买') || suggestion.includes('加')) return 'badge-buy'
  if (suggestion.includes('卖') || suggestion.includes('减')) return 'badge-sell'
  return 'badge-hold'
})
</script>

<style scoped>
.analysis-card {
  padding: 20px;
  transition: all 0.3s ease;
  border-left: 3px solid var(--border-color);
}

.analysis-card:hover {
  transform: translateY(-2px);
}

.analysis-card.suggestion-buy {
  border-left-color: #f56c6c;
}

.analysis-card.suggestion-sell {
  border-left-color: #67c23a;
}

.analysis-card.suggestion-hold {
  border-left-color: #e6a23c;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.card-icon {
  font-size: 1.5rem;
}

.card-title-group {
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
}

.card-timeframe {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.card-body {
  margin-bottom: 16px;
}

.trend-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.label {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.value {
  font-weight: 500;
}

.suggestion-row {
  margin-bottom: 12px;
}

.suggestion-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 16px;
  font-size: 0.875rem;
  font-weight: 500;
}

.badge-buy {
  background: rgba(245, 108, 108, 0.15);
  color: #f56c6c;
}

.badge-sell {
  background: rgba(103, 194, 58, 0.15);
  color: #67c23a;
}

.badge-hold {
  background: rgba(230, 162, 60, 0.15);
  color: #e6a23c;
}

.confidence-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.confidence-bar {
  flex: 1;
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-light));
  border-radius: 3px;
  transition: width 0.5s ease;
}

.confidence-value {
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 40px;
  text-align: right;
}

.card-footer {
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.reason {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
