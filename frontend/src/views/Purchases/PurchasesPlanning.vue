<template>
  <div class="planning-page">
    <div class="page-header">
      <div class="title-section">
        <h1>Планування закупівель</h1>
        <p class="subtitle">Аналіз дефіциту та формування замовлень на основі резервів виробництва</p>
      </div>
      <div class="header-actions">
        <el-button @click="fetchData" :loading="loading" circle>
          <el-icon><Refresh /></el-icon>
        </el-button>
        <el-button type="primary" @click="orderEverything" :disabled="critical.length === 0" class="bulk-btn">
          Замовити все критичне →
        </el-button>
      </div>
    </div>

    <!-- ===== BLOCK 1: CRITICAL ===== -->
    <div class="planning-section critical-section">
      <div class="section-header">
        <div class="header-tag tag-red">🔴 КРИТИЧНО — ЗАМОВИТИ ЗАРАЗ ({{ critical.length }})</div>
      </div>
      <div class="table-container">
        <el-table :data="critical" style="width: 100%" size="default" class="planning-table" v-loading="loading">
          <el-table-column label="Матеріал" min-width="250">
            <template #default="{ row }">
              <div class="prod-info">
                <span class="prod-name">{{ row.name }}</span>
                <span class="prod-sku">{{ row.sku }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Залишок" width="120" align="center">
            <template #default="{ row }">
              <span :class="{'text-danger': row.current_stock <= 0}">{{ row.current_stock }} {{ row.unit }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Зарезервовано" width="140" align="center">
            <template #default="{ row }">
              <el-tooltip content="З активних завдань на виробництво" placement="top">
                <span class="reserved-val">{{ row.reserved }} {{ row.unit }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column label="Мінімум" width="110" align="center">
            <template #default="{ row }">
              <span class="text-secondary">{{ row.min_stock }} {{ row.unit }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Замовити" width="150" align="center">
            <template #default="{ row }">
              <el-input-number v-model="row.to_order" :min="0" size="small" class="qty-input" />
            </template>
          </el-table-column>
          <el-table-column label="Постачальник" min-width="180">
            <template #default="{ row }">
              <el-select v-model="row.default_supplier_id" size="small" placeholder="Оберіть..." filterable class="supplier-select">
                <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="Дії" width="120" align="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="orderSingle(row)" plain>Замовити</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- ===== BLOCK 2: SOON ENDING ===== -->
    <div class="planning-section soon-section" v-if="soon.length > 0">
      <div class="section-header">
        <div class="header-tag tag-yellow">🟡 НЕЗАБАРОМ ЗАКІНЧУЄТЬСЯ ({{ soon.length }})</div>
      </div>
      <div class="table-container">
        <el-table :data="soon" style="width: 100%" size="default" class="planning-table" v-loading="loading">
          <el-table-column label="Матеріал" min-width="250">
            <template #default="{ row }">
              <div class="prod-info">
                <span class="prod-name">{{ row.name }}</span>
                <span class="prod-sku">{{ row.sku }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Реальний залишок" width="150" align="center">
            <template #default="{ row }">
              <div class="real-bal">
                <span class="val">{{ row.real_balance.toFixed(2) }} {{ row.unit }}</span>
                <span class="hint">Залишок - Резерв</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Мінімум" width="110" align="center">
            <template #default="{ row }">
              <span class="text-secondary">{{ row.min_stock }} {{ row.unit }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Запас (днів)" width="130" align="center">
            <template #default="{ row }">
              <span class="days-badge">~{{ row.delivery_days || 3 }} дні</span>
            </template>
          </el-table-column>
          <el-table-column label="Дії" width="120" align="right">
            <template #default="{ row }">
              <el-button type="warning" size="small" @click="orderSingle(row)" plain>Замовити</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- ===== BLOCK 3: DRAFTS ===== -->
    <div class="planning-section drafts-section" v-if="drafts.length > 0">
      <div class="section-header">
        <div class="header-tag tag-blue">📋 ЧЕРНЕТКИ ЗАМОВЛЕНЬ ({{ drafts.length }})</div>
      </div>
      <div class="table-container">
        <el-table :data="drafts" style="width: 100%" size="default" class="planning-table" v-loading="loading">
          <el-table-column label="№" width="120" prop="order_number" />
          <el-table-column label="Постачальник" min-width="200">
            <template #default="{ row }">
              {{ getSupplierName(row.supplier_id) }}
            </template>
          </el-table-column>
          <el-table-column label="Позицій" width="100" align="center" prop="line_count" />
          <el-table-column label="Сума" width="150" align="right">
            <template #default="{ row }">
              <strong>{{ formatCurrency(row.total_amount) }} ₴</strong>
            </template>
          </el-table-column>
          <el-table-column label="Дії" width="220" align="right">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="sendOrder(row)">Відправити</el-button>
              <el-button type="primary" size="small" @click="editOrder(row)" plain>Редагувати</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <div v-if="!loading && critical.length === 0 && soon.length === 0 && drafts.length === 0" class="empty-state">
      <el-empty description="Все гаразд. Дефіциту не виявлено." />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh, Warning, Check, Close, Plus, Right } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()
const loading = ref(false)
const critical = ref([])
const soon = ref([])
const drafts = ref([])
const suppliers = ref([])

const fetchData = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/v1/purchase-orders/procurement-alerts')
    critical.value = res.data.critical || []
    soon.value = res.data.soon || []
    drafts.value = res.data.drafts || []

    const sRes = await api.get('/api/v1/counterparties', { params: { is_supplier: true } })
    suppliers.value = sRes.data
  } catch (e) {
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

const getSupplierName = (id) => suppliers.value.find(s => s.id === id)?.name || '—'
const formatCurrency = (v) => new Intl.NumberFormat('uk-UA').format(v || 0)

const orderSingle = async (item) => {
  if (!item.default_supplier_id) {
    ElMessage.warning('Оберіть постачальника')
    return
  }

  try {
    loading.value = true
    const whRes = await api.get('/api/v1/warehouses')
    const whId = whRes.data.find(w => w.is_default)?.id || whRes.data[0]?.id

    const orderData = {
      supplier_id: item.default_supplier_id,
      order_date: new Date().toISOString(),
      expected_date: new Date(Date.now() + (item.delivery_days || 3) * 86400000).toISOString(),
      status: 'draft',
      warehouse_id: whId,
      currency: 'UAH',
      lines: [{
        product_id: item.product_id,
        quantity: item.to_order,
        price: 0,
        total: 0
      }]
    }

    await api.post('/api/v1/purchase-orders', orderData)
    ElMessage.success(`Створено чернетку для ${item.name}`)
    fetchData()
  } catch (e) {
    ElMessage.error('Помилка створення замовлення')
  } finally {
    loading.value = false
  }
}

const orderEverything = async () => {
  const withSupplier = critical.value.filter(a => a.default_supplier_id)
  if (withSupplier.length === 0) {
    ElMessage.warning('Вкажіть постачальників')
    return
  }

  await ElMessageBox.confirm(`Створити замовлення для ${[...new Set(withSupplier.map(a => a.default_supplier_id))].length} постачальників?`, 'Підтвердження')
  
  loading.value = true
  try {
    const whRes = await api.get('/api/v1/warehouses')
    const whId = whRes.data.find(w => w.is_default)?.id || whRes.data[0]?.id

    const grouped = {}
    withSupplier.forEach(a => {
      if (!grouped[a.default_supplier_id]) grouped[a.default_supplier_id] = []
      grouped[a.default_supplier_id].push(a)
    })

    for (const [sId, items] of Object.entries(grouped)) {
      await api.post('/api/v1/purchase-orders', {
        supplier_id: sId,
        order_date: new Date().toISOString(),
        expected_date: new Date(Date.now() + Math.max(...items.map(i => i.delivery_days || 3)) * 86400000).toISOString(),
        status: 'draft',
        warehouse_id: whId,
        currency: 'UAH',
        lines: items.map(i => ({
          product_id: i.product_id,
          quantity: i.to_order,
          price: 0,
          total: 0
        }))
      })
    }
    ElMessage.success('Замовлення згенеровані')
    fetchData()
  } catch (e) {
    ElMessage.error('Помилка')
  } finally {
    loading.value = false
  }
}

const sendOrder = async (order) => {
  try {
    await api.put(`/api/v1/purchase-orders/${order.id}`, { status: 'confirmed' })
    ElMessage.success('Замовлення підтверджено та відправлено')
    fetchData()
  } catch {
    ElMessage.error('Помилка')
  }
}

const editOrder = (order) => {
  router.push(`/purchases/orders/${order.id}`)
}

onMounted(fetchData)
</script>

<style scoped>
.planning-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.title-section h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  color: #1e293b;
}

.subtitle {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 14px;
}

.planning-section {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}

.section-header {
  padding: 16px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.header-tag {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.5px;
}

.tag-red { background: #fee2e2; color: #991b1b; }
.tag-yellow { background: #fef3c7; color: #92400e; }
.tag-blue { background: #e0e7ff; color: #3730a3; }

.table-container {
  padding: 0;
}

.planning-table :deep(th) {
  background: #fff !important;
  font-size: 12px;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
  padding: 12px 0 !important;
}

.prod-info {
  display: flex;
  flex-direction: column;
}

.prod-name {
  font-weight: 600;
  color: #1e293b;
}

.prod-sku {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 700;
}

.text-danger { color: #ef4444; font-weight: 700; }
.text-secondary { color: #64748b; font-weight: 500; }

.reserved-val {
  color: #6366f1;
  font-weight: 700;
  text-decoration: underline dotted;
  cursor: help;
}

.qty-input {
  width: 100px;
}

.days-badge {
  background: #f1f5f9;
  color: #475569;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.real-bal {
  display: flex;
  flex-direction: column;
}

.real-bal .val { font-weight: 700; color: #1e293b; }
.real-bal .hint { font-size: 10px; color: #94a3b8; }

.empty-state {
  margin-top: 60px;
}

.bulk-btn {
  font-weight: 700;
  padding: 10px 20px;
  border-radius: 10px;
}
</style>
