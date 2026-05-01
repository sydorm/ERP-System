<template>
  <div class="crm-section crm-materials-section-premium" v-if="form.product_id">
    <div class="materials-block-header">
      <div class="header-main">
        <div class="analysis-badge">Аналіз</div>
        <div class="title-group">
          <h3>Складські запаси</h3>
          <p>Перевірка наявності сировини для виконання замовлення</p>
        </div>
      </div>
      <div class="header-status">
        <div class="glass-pill" :class="materialCheck.has_issues ? 'warning' : 'success'">
          <el-icon><Check v-if="!materialCheck.has_issues" /><Warning v-else /></el-icon>
          <span>{{ materialCheck.has_issues ? 'Потрібна закупівля' : 'Запаси в нормі' }}</span>
        </div>
      </div>
    </div>

    <div v-if="materialsLoading" class="materials-loading-premium">
      <div class="loading-animation">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
      <span>Синхронізація із залишками на складі...</span>
    </div>

    <div v-else-if="materialCheck.items.length" class="materials-list-container">
      <div class="materials-grid-modern">
        <div
          v-for="item in materialCheck.items"
          :key="item.component_id"
          class="material-card-premium"
          :class="item.status"
        >
          <div class="card-glow"></div>
          <div class="m-content">
            <div class="m-header">
              <span class="m-name">{{ item.component_name }}</span>
              <div class="status-indicator"></div>
            </div>
            <div class="m-details">
              <div class="detail-item">
                <span class="label">Потрібно:</span>
                <span class="val">{{ formatQty(item.required_qty) }} {{ item.unit_of_measure }}</span>
              </div>
              <div class="detail-item stock">
                <span class="label">В наявності:</span>
                <span class="val highlight">{{ formatQty(item.available_qty) }} {{ item.unit_of_measure }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="materialCheck.has_issues" class="materials-action-banner-premium">
        <div class="banner-left">
          <div class="alert-icon">
            <el-icon><InfoFilled /></el-icon>
          </div>
          <div class="banner-text">
            <h4>Виявлено дефіцит матеріалів</h4>
            <p>Рекомендуємо сформувати замовлення постачальнику для уникнення затримок.</p>
          </div>
        </div>
        <button class="premium-action-btn" @click="$emit('go-to-purchases')">
          <span>Створити закупку</span>
          <el-icon><Promotion /></el-icon>
        </button>
      </div>
    </div>

    <div v-else class="materials-empty-premium">
      <div class="empty-icon-wrapper">
        <el-icon><DocumentDelete /></el-icon>
      </div>
      <h4>Специфікація відсутня</h4>
      <p>Для цього виробу не налаштовано склад компонентів.</p>
    </div>
  </div>
</template>

<script setup>
import { Loading, Promotion, Check, Warning, InfoFilled, DocumentDelete } from '@element-plus/icons-vue'

defineProps({
  form: { type: Object, required: true },
  materialCheck: { type: Object, required: true },
  materialsLoading: { type: Boolean, default: false },
  formatQty: { type: Function, required: true },
})

defineEmits(['go-to-purchases'])
</script>

<style scoped>
.crm-materials-section-premium {
  padding: 32px;
  background: #fff;
  border-radius: 24px;
}

.materials-block-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-main {
  display: flex;
  gap: 16px;
  align-items: center;
}

.analysis-badge {
  background: #F1F5F9;
  color: #475569;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.title-group h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 850;
  color: #0F172A;
  letter-spacing: -0.02em;
}

.title-group p {
  margin: 4px 0 0;
  font-size: 14px;
  color: #64748B;
}

.glass-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid transparent;
}

.glass-pill.success {
  background: #ECFDF5;
  color: #059669;
  border-color: #A7F3D0;
}

.glass-pill.warning {
  background: #FFFBEB;
  color: #D97706;
  border-color: #FDE68A;
}

.materials-loading-premium {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 48px;
  color: #64748B;
}

.loading-animation {
  display: flex;
  gap: 8px;
}

.dot {
  width: 10px;
  height: 10px;
  background: #6366F1;
  border-radius: 50%;
  animation: bounce 0.6s infinite alternate;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  to { transform: translateY(-10px); opacity: 0.5; }
}

.materials-grid-modern {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.material-card-premium {
  position: relative;
  background: #F8FAFC;
  border: 1px solid #F1F5F9;
  border-radius: 20px;
  padding: 24px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.material-card-premium:hover {
  transform: translateY(-4px);
  background: #fff;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.06);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
}

.ok .card-glow { background: #10B981; }
.low .card-glow { background: #F59E0B; }
.missing .card-glow { background: #EF4444; }

.m-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.m-name {
  font-size: 15px;
  font-weight: 800;
  color: #1E293B;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.ok .status-indicator { background: #10B981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.4); }
.low .status-indicator { background: #F59E0B; box-shadow: 0 0 8px rgba(245, 158, 11, 0.4); }
.missing .status-indicator { background: #EF4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }

.m-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.detail-item .label { color: #64748B; font-weight: 600; }
.detail-item .val { color: #1E293B; font-weight: 750; }

.detail-item.stock .val.highlight {
  color: #10B981;
}

.missing .detail-item.stock .val.highlight {
  color: #EF4444;
}

.materials-action-banner-premium {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  background: linear-gradient(135deg, #FFFBEB 0%, #FFF8E1 100%);
  border: 1px solid #FEF3C7;
  border-radius: 24px;
  gap: 24px;
}

.banner-left {
  display: flex;
  gap: 20px;
  align-items: center;
}

.alert-icon {
  width: 48px;
  height: 48px;
  background: #FEF3C7;
  color: #D97706;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 24px;
}

.banner-text h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  color: #92400E;
}

.banner-text p {
  margin: 4px 0 0;
  font-size: 13px;
  color: #B45309;
  font-weight: 600;
}

.premium-action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 28px;
  background: #D97706;
  color: #fff;
  border: none;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 8px 20px rgba(217, 119, 6, 0.2);
}

.premium-action-btn:hover {
  background: #B45309;
  transform: translateY(-2px);
  box-shadow: 0 12px 25px rgba(217, 119, 6, 0.3);
}

.materials-empty-premium {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 64px;
  text-align: center;
}

.empty-icon-wrapper {
  width: 64px;
  height: 64px;
  background: #F1F5F9;
  color: #94A3B8;
  border-radius: 20px;
  display: grid;
  place-items: center;
  font-size: 32px;
  margin-bottom: 20px;
}

.materials-empty-premium h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: #1E293B;
}

.materials-empty-premium p {
  margin: 8px 0 0;
  font-size: 14px;
  color: #64748B;
  font-weight: 600;
}

@media (max-width: 992px) {
  .materials-action-banner-premium {
    flex-direction: column;
    text-align: center;
  }
  .banner-left { flex-direction: column; }
  .premium-action-btn { width: 100%; justify-content: center; }
}
</style>
