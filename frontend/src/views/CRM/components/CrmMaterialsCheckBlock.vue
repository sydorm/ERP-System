<template>
  <div class="crm-section crm-materials-section" v-if="form.product_id">
    <div class="materials-block-head">
      <div class="materials-title-block">
        <span class="materials-kicker">Склад · Аналіз</span>
        <h3>Наявність матеріалів</h3>
      </div>
      <div class="materials-status-badge">
        <span class="status-badge-modern" :class="materialCheck.has_issues ? 'warning' : 'success'">
          <el-icon><Check v-if="!materialCheck.has_issues" /><Warning v-else /></el-icon>
          {{ materialCheck.has_issues ? 'Потрібне дозамовлення' : 'Матеріалів достатньо' }}
        </span>
      </div>
    </div>

    <div v-if="materialsLoading" class="materials-loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>Аналізуємо запаси на складі...</span>
    </div>

    <div v-else-if="materialCheck.items.length" class="materials-list-container">
      <div class="materials-grid-modern">
        <div
          v-for="item in materialCheck.items"
          :key="item.component_id"
          class="material-card-modern"
          :class="item.status"
        >
          <div class="m-main">
            <span class="m-name">{{ item.component_name }}</span>
            <span class="m-req">Потрібно: {{ formatQty(item.required_qty) }} {{ item.unit_of_measure }}</span>
          </div>
          <div class="m-stock">
            <span class="m-stock-val">{{ formatQty(item.available_qty) }}</span>
            <span class="m-stock-label">в наявності</span>
          </div>
        </div>
      </div>

      <div v-if="materialCheck.has_issues" class="materials-order-banner">
        <div class="banner-text">
          <el-icon><InfoFilled /></el-icon>
          <span>Виявлено дефіцит деяких позицій. Рекомендуємо створити замовлення постачальнику.</span>
        </div>
        <button class="banner-btn" @click="$emit('go-to-purchases')">
          <el-icon><Promotion /></el-icon>
          Створити закупку
        </button>
      </div>
    </div>
    <div v-else class="materials-empty-state">
      <el-icon><DocumentDelete /></el-icon>
      <p>Для обраного виробу не знайдено активної специфікації.</p>
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
.crm-materials-section {
  padding: 24px;
}

.materials-block-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.materials-kicker {
  display: inline-flex;
  margin-bottom: 6px;
  color: #64748B;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.materials-title-block h3 {
  margin: 0;
  color: #0F172A;
  font-size: 20px;
  font-weight: 800;
}

.status-badge-modern {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 700;
}

.status-badge-modern.success { background: #ECFDF5; color: #059669; }
.status-badge-modern.warning { background: #FFFBEB; color: #D97706; }

.materials-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: #64748B;
  font-size: 14px;
}

.materials-loading-state .el-icon { font-size: 32px; color: #6366F1; }

.materials-grid-modern {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.material-card-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: #F8FAFC;
  border-radius: 14px;
  border: 1px solid #F1F5F9;
  transition: all 0.2s;
}

.material-card-modern:hover { transform: translateY(-1px); border-color: #E2E8F0; }

.material-card-modern.ok { border-left: 4px solid #10B981; }
.material-card-modern.low { border-left: 4px solid #F59E0B; }
.material-card-modern.missing { border-left: 4px solid #EF4444; background: #FFF1F2; }

.m-main { display: flex; flex-direction: column; gap: 4px; }
.m-name { font-size: 13px; font-weight: 700; color: #1E293B; }
.m-req { font-size: 11px; color: #64748B; font-weight: 600; }

.m-stock { text-align: right; }
.m-stock-val { display: block; font-size: 16px; font-weight: 800; color: #0F172A; }
.m-stock-label { font-size: 9px; color: #94A3B8; text-transform: uppercase; font-weight: 800; }

.material-card-modern.missing .m-stock-val { color: #EF4444; }

.materials-order-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #FFFBEB;
  border: 1px solid #FEF3C7;
  border-radius: 16px;
  gap: 16px;
}

.banner-text { display: flex; align-items: center; gap: 10px; font-size: 13px; color: #92400E; font-weight: 600; }
.banner-text .el-icon { font-size: 20px; }

.banner-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 10px;
  background: #D97706;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.banner-btn:hover { background: #B45309; transform: translateY(-1px); }

.materials-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: #94A3B8;
  text-align: center;
}

.materials-empty-state .el-icon { font-size: 40px; margin-bottom: 12px; }
.materials-empty-state p { font-size: 14px; margin: 0; }
</style>
