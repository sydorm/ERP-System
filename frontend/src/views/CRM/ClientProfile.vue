<template>
  <el-drawer
    v-model="drawerVisible"
    title="Профіль клієнта"
    size="480px"
    :before-close="handleClose"
    class="client-profile-drawer"
  >
    <div v-loading="loading" class="profile-content">
      <div v-if="client.id">
        <!-- Header Info -->
        <div class="client-header">
          <h2 class="client-name">{{ client.name }}</h2>
          <p class="client-phone">📞 {{ client.phone || 'Немає телефону' }}</p>
          <el-tag size="small" type="info" effect="plain">Канал: {{ client.channel }}</el-tag>
        </div>

        <el-divider />

        <!-- Stats Grid -->
        <div class="stats-grid">
          <div class="stat-box">
            <span class="stat-label">LTV</span>
            <span class="stat-value dm-mono">{{ formatCurrency(client.ltv) }}</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">Замовлень</span>
            <span class="stat-value dm-mono">{{ client.orders_count }}</span>
          </div>
        </div>

        <div class="last-action-box">
          <span class="stat-label">Остання дія:</span>
          <span class="stat-value action-text">{{ client.last_action }}</span>
          <span v-if="client.last_action_at" class="action-time dm-mono">{{ formatTime(client.last_action_at) }}</span>
        </div>

        <el-divider />

        <!-- Notes -->
        <div class="section-title">Нотатки менеджера</div>
        <el-input
          v-model="client.notes"
          type="textarea"
          :rows="4"
          placeholder="Додайте нотатки про клієнта..."
          @blur="saveNotes"
        />

        <el-divider />

        <!-- Order History -->
        <div class="section-title">Історія замовлень</div>
        <el-table :data="client.orders" style="width: 100%" size="small">
          <el-table-column prop="order_number" label="№" width="100">
            <template #default="scope">
              <el-link type="primary" @click="openOrder(scope.row.id)">#{{ scope.row.order_number }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="crm_stage" label="Статус">
            <template #default="scope">
              <el-tag size="small" :type="getStageTagType(scope.row.crm_stage)">
                {{ mapStageName(scope.row.crm_stage) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_amount" label="Сума" align="right">
            <template #default="scope">
              <span class="dm-mono">{{ formatCurrency(scope.row.total_amount) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-else description="Клієнта не знайдено" />
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useRouter } from 'vue-router'

const props = defineProps({
  clientId: {
    type: String,
    default: null
  },
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])
const router = useRouter()

const drawerVisible = ref(false)
const loading = ref(false)
const client = ref({})

watch(() => props.modelValue, (val) => {
  drawerVisible.value = val
  if (val && props.clientId) {
    fetchProfile()
  }
})

watch(() => drawerVisible.value, (val) => {
  emit('update:modelValue', val)
})

const fetchProfile = async () => {
  loading.value = true
  try {
    const res = await api.get(`/api/v1/crm/clients/${props.clientId}/profile`)
    client.value = res.data
  } catch (e) {
    console.error(e)
    ElMessage.error('Помилка завантаження профілю клієнта')
  } finally {
    loading.value = false
  }
}

const handleClose = (done) => {
  done()
}

const saveNotes = async () => {
  try {
    await api.put(`/api/v1/counterparties/${props.clientId}`, { notes: client.value.notes })
    ElMessage.success('Нотатки збережено')
  } catch (e) {
    console.error(e)
    ElMessage.error('Помилка збереження нотаток')
  }
}

const openOrder = (orderId) => {
  drawerVisible.value = false
  router.push(`/crm/orders/${orderId}`)
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('uk-UA', {
    style: 'currency',
    currency: 'UAH',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value || 0)
}

const formatTime = (dateString) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleString('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const mapStageName = (stage) => {
  const maps = {
    'new': 'Нові',
    'payment': 'Оплата',
    'processing': 'Обробка',
    'production': 'Виробництво',
    'done': 'Завершено',
    'cancelled': 'Скасовано'
  }
  return maps[stage] || stage
}

const getStageTagType = (stage) => {
  const maps = {
    'new': 'info',
    'payment': 'warning',
    'processing': 'primary',
    'production': 'success',
    'done': 'success',
    'cancelled': 'danger'
  }
  return maps[stage] || 'info'
}
</script>

<style scoped>
.profile-content {
  padding: 10px;
}
.client-header {
  margin-bottom: 15px;
}
.client-name {
  margin: 0 0 5px 0;
  font-size: 20px;
  color: #1E293B;
}
.client-phone {
  margin: 0 0 10px 0;
  color: #64748B;
}
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
}
.stat-box {
  background: #F8FAFC;
  padding: 12px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}
.stat-label {
  font-size: 12px;
  color: #64748B;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #0F172A;
}
.last-action-box {
  background: #F8FAFC;
  padding: 12px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  margin-top: 10px;
}
.action-text {
  font-size: 14px;
  font-weight: 500;
}
.action-time {
  font-size: 11px;
  color: #94A3B8;
  margin-top: 4px;
}
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 10px;
}
.dm-mono {
  font-family: 'DM Mono', monospace;
}
</style>
