<template>
  <div v-if="alerts.length > 0" class="procurement-alerts-card shadow-lg mb-6">
    <div class="card-header">
      <div class="header-left">
        <el-icon class="alert-icon pulse"><Warning /></el-icon>
        <div class="title-group">
          <h3>ПОТРІБНО ЗАМОВИТИ ({{ alerts.length }})</h3>
          <p>Система виявила дефіцит залишків по {{ alerts.length }} позиціям</p>
        </div>
      </div>
      <div class="header-right">
        <el-button 
            type="primary" 
            class="batch-order-btn" 
            @click="orderEverything"
            :loading="bulkOrdering"
        >
          Замовити все в один клік
        </el-button>
        <el-button circle :icon="Close" @click="isVisible = false" class="close-btn" />
      </div>
    </div>

    <div class="alerts-table-container">
      <el-table :data="alerts" style="width: 100%" size="small" class="alerts-table">
        <el-table-column label="Товар" min-width="250">
          <template #default="{ row }">
            <div class="product-cell">
              <span class="product-sku">{{ row.sku }}</span>
              <span class="product-name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Зараз" width="120" align="center">
          <template #default="{ row }">
            <el-tag type="danger" effect="plain" class="qty-tag">
              {{ row.current_stock }} {{ row.unit }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="Мінімум" width="120" align="center">
          <template #default="{ row }">
             <span class="threshold-val">{{ row.min_stock }} {{ row.unit }}</span>
          </template>
        </el-table-column>

        <el-table-column label="До замовлення" width="150" align="center">
          <template #default="{ row }">
            <el-input-number 
                v-model="row.to_order" 
                size="small" 
                controls-position="right" 
                :min="0.001"
                class="order-qty-input"
            />
          </template>
        </el-table-column>

        <el-table-column label="Постачальник" min-width="200">
          <template #default="{ row }">
            <el-select 
                v-model="row.default_supplier_id" 
                size="small" 
                placeholder="Оберіть..." 
                class="supplier-select"
                filterable
            >
               <el-option
                  v-for="s in suppliers"
                  :key="s.id"
                  :label="s.name"
                  :value="s.id"
               />
            </el-select>
          </template>
        </el-table-column>

        <el-table-column width="100" align="right">
          <template #default="{ row }">
            <el-button 
                type="primary" 
                plain 
                size="small" 
                class="order-row-btn"
                @click="orderSingle(row)"
            >
              Замовити
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Warning, Close } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const alerts = ref([])
const suppliers = ref([])
const bulkOrdering = ref(false)
const isVisible = ref(true)

const emit = defineEmits(['order-created'])

const fetchAlerts = async () => {
  try {
    const res = await api.get('/api/v1/purchase-orders/procurement-alerts')
    alerts.value = res.data
  } catch (e) {
    console.error('Failed to fetch procurement alerts', e)
  }
}

const fetchSuppliers = async () => {
  try {
    const res = await api.get('/api/v1/counterparties', { params: { is_supplier: true } })
    suppliers.value = res.data
  } catch (e) {
    console.error('Failed to fetch suppliers', e)
  }
}

const orderSingle = async (item) => {
    if (!item.default_supplier_id) {
        ElMessage.warning('Оберіть постачальника для цього товару')
        return
    }

    try {
        // Create a single purchase order
        const orderData = {
            supplier_id: item.default_supplier_id,
            order_date: new Date().toISOString(),
            expected_date: new Date(Date.now() + (item.delivery_days || 3) * 86400000).toISOString(),
            status: 'draft',
            warehouse_id: null, // User will pick in editor or we use default company warehouse
            currency: 'UAH',
            total_amount: 0, // Backend or JS can calc
            lines: [
                {
                    product_id: item.product_id,
                    quantity: item.to_order,
                    price: 0, // Placeholder
                    total: 0
                }
            ]
        }

        // Get default warehouse for company
        const whRes = await api.get('/api/v1/warehouses')
        if (whRes.data.length > 0) {
            orderData.warehouse_id = whRes.data[0].id
        }

        await api.post('/api/v1/purchase-orders', orderData)
        ElMessage.success(`Створено замовлення на ${item.name}`)
        fetchAlerts()
        emit('order-created')
    } catch (e) {
        ElMessage.error('Помилка при створенні замовлення')
    }
}

const orderEverything = async () => {
    const withSupplier = alerts.value.filter(a => a.default_supplier_id)
    if (withSupplier.length === 0) {
        ElMessage.warning('Вкажіть постачальників хоча б для декількох позицій')
        return
    }

    await ElMessageBox.confirm(
        `Буде створено окремі замовлення для кожного постачальника (${[...new Set(withSupplier.map(a => a.default_supplier_id))].length}). Продовжити?`,
        'Групове замовлення',
        { confirmButtonText: 'Так', cancelButtonText: 'Ні', type: 'info' }
    )

    bulkOrdering.value = true
    try {
        // Group by supplier
        const bySupplier = {}
        withSupplier.forEach(a => {
            if (!bySupplier[a.default_supplier_id]) bySupplier[a.default_supplier_id] = []
            bySupplier[a.default_supplier_id].push(a)
        })

        // Get default warehouse
        const whRes = await api.get('/api/v1/warehouses')
        const whId = whRes.data.length > 0 ? whRes.data[0].id : null

        for (const [sId, items] of Object.entries(bySupplier)) {
            const orderData = {
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
            }
            await api.post('/api/v1/purchase-orders', orderData)
        }

        ElMessage.success('Замовлення успішно згенеровані')
        fetchAlerts()
        emit('order-created')
    } catch (e) {
        ElMessage.error('Виникла помилка під час обробки')
    } finally {
        bulkOrdering.value = false
    }
}

onMounted(() => {
  fetchAlerts()
  fetchSuppliers()
})
</script>

<style scoped>
.procurement-alerts-card {
  background: linear-gradient(135deg, #fff9f0 0%, #ffffff 100%);
  border-radius: 16px;
  border: 1px solid #ffedd5;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff8f1;
  border-bottom: 1px solid #ffedd5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.alert-icon {
  font-size: 28px;
  color: #f97316;
}

.title-group h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 800;
  color: #9a3412;
  letter-spacing: 0.5px;
}

.title-group p {
  margin: 2px 0 0;
  font-size: 12px;
  color: #ea580c;
  opacity: 0.8;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.batch-order-btn {
  background: linear-gradient(135deg, #f97316, #fb923c);
  border: none;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.25);
}

.batch-order-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(249, 115, 22, 0.35);
}

.close-btn {
  border: none;
  background: transparent;
  color: #94a3b8;
}

.close-btn:hover {
  background: #ffedd5;
  color: #9a3412;
}

/* Table styling */
.alerts-table-container {
  padding: 0;
}

.alerts-table :deep(th) {
  background: transparent !important;
  font-size: 11px;
  font-weight: 700;
  color: #9a3412;
  border-bottom: 1px solid #ffedd5 !important;
}

.alerts-table :deep(td) {
  padding: 10px 0 !important;
  border-bottom: 1px solid #fff2e6 !important;
}

.product-cell {
  display: flex;
  flex-direction: column;
}

.product-sku {
  font-size: 10px;
  font-weight: 700;
  color: #f97316;
  text-transform: uppercase;
}

.product-name {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.qty-tag {
  font-weight: 700;
  border-radius: 8px;
}

.threshold-val {
  font-weight: 600;
  color: #64748b;
  font-size: 12px;
}

.order-qty-input {
  width: 90px;
}

.supplier-select {
  width: 100%;
}

.order-row-btn {
  font-weight: 700;
}

/* Animations */
.pulse {
  animation: pulse-animation 2s infinite;
}

@keyframes pulse-animation {
  0% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
  100% { opacity: 1; transform: scale(1); }
}

.shadow-lg {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
}
</style>
