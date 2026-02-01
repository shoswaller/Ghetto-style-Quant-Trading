<template>
  <div class="app-container gradient-bg">
    <header class="app-header glass-card">
      <div class="header-content">
        <div class="logo">
          <el-icon :size="28" color="#409eff"><TrendCharts /></el-icon>
          <h1>丐版量化交易</h1>
        </div>
        <nav class="nav-links">
          <router-link to="/" class="nav-link" active-class="active">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </router-link>
          <router-link to="/diagnosis" class="nav-link" active-class="active">
            <el-icon><DataAnalysis /></el-icon>
            <span>个股诊断</span>
          </router-link>
        </nav>
        <div class="header-actions">
          <el-badge :value="llmStatus" :type="llmStatusType" class="status-badge">
            <el-button :icon="Connection" circle />
          </el-badge>
        </div>
      </div>
    </header>
    
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    
    <footer class="app-footer">
      <p>丐版量化交易系统 © 2026 | 仅供学习研究使用</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Connection, HomeFilled, DataAnalysis, TrendCharts } from '@element-plus/icons-vue'
import { checkHealth } from '@/api/stock'

const isConnected = ref(false)

const llmStatus = computed(() => isConnected.value ? '在线' : '离线')
const llmStatusType = computed(() => isConnected.value ? 'success' : 'danger')

onMounted(async () => {
  try {
    const res = await checkHealth()
    isConnected.value = res.status === 'ok'
  } catch {
    isConnected.value = false
  }
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0 24px;
  margin: 16px;
  margin-bottom: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo h1 {
  font-size: 1.25rem;
  font-weight: 600;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: var(--text-primary);
  background: rgba(64, 158, 255, 0.1);
}

.nav-link.active {
  color: var(--primary-color);
  background: rgba(64, 158, 255, 0.15);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-badge :deep(.el-badge__content) {
  font-size: 10px;
}

.app-main {
  flex: 1;
  padding: 24px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

.app-footer {
  padding: 24px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.875rem;
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
