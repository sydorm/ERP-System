<template>
  <div class="bp-rules-page">
    <div class="bp-header">
      <div class="bp-header-left">
        <h2 class="bp-title">Налаштування бізнес-процесів</h2>
        <p class="bp-subtitle">Правила автоматичного створення документів</p>
      </div>
      <el-button type="primary" @click="openEditor(null)">
        <el-icon><Plus /></el-icon> Нове правило
      </el-button>
    </div>

    <div class="bp-table-card" v-loading="loading">
      <el-table :data="rules" border stripe>
        <el-table-column label="Назва правила" min-width="220">
          <template #default="{ row }">
            <div class="rule-name-cell">
              <span class="rule-name">{{ row.name }}</span>
              <p class="rule-desc" v-if="row.description">{{ row.description }}</p>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Подія" min-width="220">
          <template #default="{ row }">
            <div class="event-cell">
              <span class="event-source">{{ SOURCE_LABELS[row.source_type] || row.source_type }}</span>
              <el-icon class="event-arrow"><ArrowRight /></el-icon>
              <span class="event-status">{{ STATUS_LABELS[row.to_status] || row.to_status }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Дія" width="200">
          <template #default="{ row }">
            <span class="action-label">{{ ACTION_LABELS[row.action_type] || row.action_type }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Режим" width="190" align="center">
          <template #default="{ row }">
            <span class="mode-badge" :class="`mode-${row.mode}`">
              {{ MODE_LABELS[row.mode] || row.mode }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="Активність" width="120" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="row.is_active"
              @change="toggleRule(row)"
              active-color="#22C55E"
              inactive-color="#CBD5E1"
            />
          </template>
        </el-table-column>

        <el-table-column label="Оновлено" width="130" align="center">
          <template #default="{ row }">
            <span class="date-label">{{ formatDate(row.updated_at) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Дії" width="100" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditor(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Rule Editor Dialog -->
    <BusinessProcessRuleEditor
      v-model="editorVisible"
      :rule="editingRule"
      @saved="fetchRules"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Edit, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import BusinessProcessRuleEditor from './BusinessProcessRuleEditor.vue'

const rules = ref([])
const loading = ref(false)
const editorVisible = ref(false)
const editingRule = ref(null)

const SOURCE_LABELS = {
  crm_lead: 'CRM-заявка',
  customer_order: 'Замовлення покупця',
  production_task: 'Виробниче завдання',
  sales_invoice: 'Видаткова накладна',
}
const STATUS_LABELS = {
  processing: 'В роботі',
  completed: 'Готово',
  done: 'Виконано',
  production: 'Виробництво',
  payment: 'Оплата',
  new: 'Нове',
}
const ACTION_LABELS = {
  create_customer_order: 'Створити Замовлення покупця',
  create_sales_invoice: 'Створити Видаткову накладну',
  create_invoice: 'Створити Рахунок на оплату',
  create_production_task: 'Створити Виробниче завдання',
  reserve_materials: 'Зарезервувати матеріали',
}
const MODE_LABELS = {
  automatic: 'Автоматично',
  ask_confirmation: 'Запитувати',
  disabled: 'Вимкнено',
}

const fetchRules = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/v1/business-process/rules')
    rules.value = res.data
  } catch {
    ElMessage.error('Помилка завантаження правил')
  } finally {
    loading.value = false
  }
}

const toggleRule = async (row) => {
  try {
    const res = await api.patch(`/api/v1/business-process/rules/${row.id}/toggle`)
    row.is_active = res.data.is_active
    ElMessage.success(row.is_active ? 'Правило активовано' : 'Правило вимкнено')
  } catch {
    ElMessage.error('Помилка зміни стану')
  }
}

const openEditor = (rule) => {
  editingRule.value = rule ? { ...rule } : null
  editorVisible.value = true
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('uk-UA') : '—'

onMounted(fetchRules)
</script>

<style scoped>
.bp-rules-page {
  padding: 28px 32px;
  background: #F8FAFC;
  min-height: calc(100vh - 60px);
}
.bp-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.bp-title {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 700;
  color: #1E293B;
}
.bp-subtitle {
  margin: 0;
  font-size: 13px;
  color: #64748B;
}
.bp-table-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  overflow: hidden;
}
.rule-name { font-weight: 600; color: #1E293B; font-size: 14px; }
.rule-desc { font-size: 12px; color: #94A3B8; margin: 2px 0 0; }
.event-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}
.event-source { font-weight: 600; color: #3B82F6; }
.event-arrow { color: #94A3B8; font-size: 12px; }
.event-status { font-weight: 600; color: #22C55E; }
.action-label { font-size: 13px; color: #334155; }
.date-label { font-size: 12px; color: #94A3B8; }

.mode-badge {
  display: inline-flex;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}
.mode-automatic   { background: #F0FDF4; color: #16A34A; }
.mode-ask_confirmation { background: #EFF6FF; color: #3B82F6; }
.mode-disabled    { background: #F1F5F9; color: #94A3B8; }
</style>
