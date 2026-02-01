<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="gradient-text">智能股票分析</span>
          <br />
          助力您的投资决策
        </h1>
        <p class="hero-description">
          结合本地AI与云端AI的双重能力，为您提供专业的个股诊断与操作建议
        </p>
        <div class="hero-actions">
          <router-link to="/diagnosis">
            <el-button type="primary" size="large" :icon="DataAnalysis">
              开始诊断
            </el-button>
          </router-link>
        </div>
      </div>
      
      <div class="hero-visual">
        <div class="chart-preview glass-card">
          <div class="chart-header">
            <span class="stock-name">平安银行</span>
            <span class="stock-code">000001</span>
          </div>
          <div class="chart-body">
            <div class="chart-line"></div>
            <div class="chart-data">
              <span class="price">¥12.35</span>
              <span class="change price-up">+1.23%</span>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <section class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <div class="feature-card glass-card">
          <div class="feature-icon">
            <el-icon :size="32" color="#409eff"><TrendCharts /></el-icon>
          </div>
          <h3>个股诊断</h3>
          <p>输入股票代码，获取当日、本周、长线的操作建议</p>
          <div class="feature-tag mvp-tag">MVP</div>
        </div>
        
        <div class="feature-card glass-card disabled">
          <div class="feature-icon">
            <el-icon :size="32" color="#909399"><Filter /></el-icon>
          </div>
          <h3>选股筛选</h3>
          <p>根据自定义策略筛选符合条件的股票</p>
          <div class="feature-tag coming-tag">待开发</div>
        </div>
        
        <div class="feature-card glass-card disabled">
          <div class="feature-icon">
            <el-icon :size="32" color="#909399"><Histogram /></el-icon>
          </div>
          <h3>热门扫描</h3>
          <p>扫描热门板块和热点股票</p>
          <div class="feature-tag coming-tag">待开发</div>
        </div>
        
        <div class="feature-card glass-card disabled">
          <div class="feature-icon">
            <el-icon :size="32" color="#909399"><Document /></el-icon>
          </div>
          <h3>操作记录</h3>
          <p>记录您的交易操作和持仓情况</p>
          <div class="feature-tag coming-tag">待开发</div>
        </div>
      </div>
    </section>
    
    <section class="tech-section">
      <h2 class="section-title">技术架构</h2>
      <div class="tech-cards">
        <div class="tech-card glass-card">
          <div class="tech-icon">🖥️</div>
          <h4>局域网AI</h4>
          <p>Nemotron-30B via llama.cpp</p>
          <span class="tech-role">数据处理与结构化</span>
        </div>
        <div class="tech-arrow">→</div>
        <div class="tech-card glass-card">
          <div class="tech-icon">☁️</div>
          <h4>云端AI</h4>
          <p>DeepSeek-V3</p>
          <span class="tech-role">智能分析与决策</span>
        </div>
        <div class="tech-arrow">→</div>
        <div class="tech-card glass-card">
          <div class="tech-icon">📊</div>
          <h4>数据源</h4>
          <p>AKShare</p>
          <span class="tech-role">实时股票数据</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { DataAnalysis, TrendCharts, Filter, Histogram, Document } from '@element-plus/icons-vue'
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
}

/* Hero Section */
.hero-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
  padding: 48px 0;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 24px;
}

.gradient-text {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 50%, #a0cfff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.125rem;
  color: var(--text-secondary);
  margin-bottom: 32px;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.hero-visual {
  display: flex;
  justify-content: center;
}

.chart-preview {
  width: 300px;
  padding: 24px;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.chart-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.stock-name {
  font-weight: 600;
}

.stock-code {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.chart-body {
  padding: 24px 0;
}

.chart-line {
  height: 80px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(64, 158, 255, 0.1) 20%,
    rgba(64, 158, 255, 0.2) 40%,
    rgba(64, 158, 255, 0.3) 60%,
    rgba(64, 158, 255, 0.2) 80%,
    transparent 100%
  );
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.chart-line::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    var(--primary-color) 0%, 
    var(--primary-light) 50%,
    var(--primary-color) 100%
  );
  animation: wave 3s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% { transform: translateY(0) scaleY(1); }
  25% { transform: translateY(-10px) scaleY(0.8); }
  50% { transform: translateY(5px) scaleY(1.2); }
  75% { transform: translateY(-5px) scaleY(0.9); }
}

.chart-data {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-top: 16px;
}

.price {
  font-size: 1.5rem;
  font-weight: 600;
}

.change {
  font-size: 1rem;
}

/* Features Section */
.features-section {
  padding: 64px 0;
}

.section-title {
  font-size: 1.75rem;
  text-align: center;
  margin-bottom: 48px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.feature-card {
  padding: 32px 24px;
  text-align: center;
  position: relative;
  transition: all 0.3s ease;
}

.feature-card:not(.disabled):hover {
  transform: translateY(-4px);
  border-color: var(--primary-color);
}

.feature-card.disabled {
  opacity: 0.6;
}

.feature-icon {
  margin-bottom: 16px;
}

.feature-card h3 {
  font-size: 1.125rem;
  margin-bottom: 8px;
}

.feature-card p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.6;
}

.feature-tag {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.mvp-tag {
  background: rgba(64, 158, 255, 0.2);
  color: var(--primary-color);
}

.coming-tag {
  background: rgba(144, 147, 153, 0.2);
  color: var(--text-muted);
}

/* Tech Section */
.tech-section {
  padding: 64px 0;
}

.tech-cards {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
}

.tech-card {
  padding: 32px;
  text-align: center;
  min-width: 200px;
}

.tech-icon {
  font-size: 2.5rem;
  margin-bottom: 16px;
}

.tech-card h4 {
  font-size: 1.125rem;
  margin-bottom: 8px;
}

.tech-card p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 12px;
}

.tech-role {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(64, 158, 255, 0.1);
  color: var(--primary-color);
  border-radius: 12px;
  font-size: 0.75rem;
}

.tech-arrow {
  font-size: 1.5rem;
  color: var(--text-muted);
}

/* 响应式 */
@media (max-width: 1024px) {
  .hero-section {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-actions {
    justify-content: center;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .tech-cards {
    flex-direction: column;
  }
  
  .tech-arrow {
    transform: rotate(90deg);
  }
}

@media (max-width: 640px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>
