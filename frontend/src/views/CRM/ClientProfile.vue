<template>
  <el-drawer
    v-model="drawerVisible"
    title="Профіль клієнта"
    size="480px"
    :before-close="handleClose"
    class="client-profile-drawer"
  >
    <div v-loading="loading" class="profile-content" style="padding: 0;">
      <div v-if="client.id">
        <!-- Header Info -->
        <div class="client-header saas-gradient-header" style="padding: 24px; border-radius: 0 0 24px 24px; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(20, 99, 255, 0.15);">
          <h2 class="client-name" style="color: #fff; margin-bottom: 8px; font-size: 24px;">{{ client.name }}</h2>
          <p class="client-phone" style="color: rgba(255,255,255,0.85); font-size: 15px; margin-bottom: 12px;">📞 {{ client.phone || 'Немає телефону' }}</p>
          <div style="display: flex; gap: 8px;">
            <el-tag size="small" effect="dark" style="background: rgba(255,255,255,0.2); border: none; color: #fff;">Канал: {{ client.channel }}</el-tag>
          </div>
        </div>

        <div style="padding: 0 24px 24px;">
          <!-- Stats Grid -->
          <div class="stats-grid" style="margin-bottom: 24px;">
            <div class="stat-box saas-glass-card" style="padding: 16px;">
              <span class="stat-label">LTV</span>
              <span class="stat-value dm-mono" style="color: #1463FF;">{{ formatCurrency(client.ltv) }}</span>
            </div>
            <div class="stat-box saas-glass-card" style="padding: 16px;">
              <span class="stat-label">Замовлень</span>
              <span class="stat-value dm-mono">{{ client.orders_count }}</span>
            </div>
          </div>

          <div class="last-action-box saas-glass-card" style="padding: 16px; margin-bottom: 24px;">
            <span class="stat-label">Остання дія:</span>
            <span class="stat-value action-text">{{ client.last_action }}</span>
            <span v-if="client.last_action_at" class="action-time dm-mono">{{ formatTime(client.last_action_at) }}</span>
          </div>

          <!-- Notes -->
          <div class="section-title">Нотатки менеджера</div>
          <el-input
            v-model="client.notes"
            type="textarea"
            :rows="4"
            placeholder="Додайте нотатки про клієнта..."
            style="margin-bottom: 24px;"
            @blur="saveNotes"
          />

          <!-- Order History -->
          <div class="section-title">Історія замовлень</div>
          <el-table :data="client.orders" style="width: 100%; border-radius: 12px; overflow: hidden;" size="small" class="saas-glass-card">
            <el-table-column prop="order_number" label="№" width="100">
              <template #default="scope">
                <el-link type="primary" @click="openOrder(scope.row.id)" style="font-weight: 700;">#{{ scope.row.order_number }}</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="crm_stage" label="Статус">
              <template #default="scope">
                <el-tag size="small" :type="getStageTagType(scope.row.crm_stage)" effect="light" style="border-radius: 6px;">
                  {{ mapStageName(scope.row.crm_stage) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_amount" label="Сума" align="right">
              <template #default="scope">
                <span class="dm-mono" style="font-weight: 700;">{{ formatCurrency(scope.row.total_amount) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
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
