<template>
  <div class="payroll-manager">
    <!-- Top Summary -->
    <div class="summary-cards">
      <el-card shadow="hover" class="summary-card accrued">
        <template #header>Нараховано (місяць)</template>
        <div class="value">{{ formatCurrency(totalAccruedMonth) }} ₴</div>
      </el-card>
      <el-card shadow="hover" class="summary-card paid">
        <template #header>Виплачено (місяць)</template>
        <div class="value">{{ formatCurrency(totalPaidMonth) }} ₴</div>
      </el-card>
      <el-card shadow="hover" class="summary-card balance">
        <template #header>Загальний борг перед персоналом</template>
        <div class="value">{{ formatCurrency(totalBalance) }} ₴</div>
      </el-card>
    </div>

    <!-- Main Content -->
    <el-tabs v-model="activeTab" class="payroll-tabs">
      <!-- BALANCES TAB -->
      <el-tab-pane label="Баланс та виплати" name="balances">
        <div class="tab-header">
          <div class="filters">
            <el-input 
              v-model="searchQuery" 
              placeholder="Пошук співробітника..." 
              clearable 
              style="width: 300px"
            />
          </div>
          <div class="actions">
            <el-button type="primary" :icon="Plus" @click="handleNewTransaction('ACCRUAL')">
              Нарахувати
            </el-button>
            <el-button type="success" :icon="Wallet" @click="handleNewTransaction('PAYMENT')">
              Виплатити
            </el-button>
          </div>
        </div>

        <el-table :data="filteredBalances" v-loading="loading">
          <el-table-column prop="full_name" label="Співробітник" min-width="200" />
          <el-table-column prop="department_name" label="Підрозділ" width="180" />
          <el-table-column label="Нараховано" width="150" align="right">
            <template #default="{ row }">
              <span class="accrued-text">{{ formatCurrency(row.total_accrued) }} ₴</span>
            </template>
          </el-table-column>
          <el-table-column label="Виплачено" width="150" align="right">
            <template #default="{ row }">
              <span class="paid-text">{{ formatCurrency(row.total_paid) }} ₴</span>
            </template>
          </el-table-column>
          <el-table-column label="Поточний баланс" width="180" align="right">
            <template #default="{ row }">
              <el-tag :type="row.balance > 0 ? 'danger' : 'success'" effect="dark">
                {{ formatCurrency(row.balance) }} ₴
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Дії" width="120" align="center">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewHistory(row.employee_id)">
                Історія
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- HISTORY TAB -->
      <el-tab-pane label="Історія транзакцій" name="history">
        <div class="tab-header">
          <div class="filters">
            <el-date-picker
              v-model="historyRange"
              type="daterange"
              range-separator="-"
              start-placeholder="З"
              end-placeholder="По"
              style="width: 300px"
              @change="fetchHistory"
            />
          </div>
        </div>

        <el-table :data="history" v-loading="loadingHistory">
          <el-table-column prop="date" label="Дата" width="120" />
          <el-table-column prop="employee_name" label="Співробітник" min-width="180" v-if="!currentEmpFilter" />
          <el-table-column prop="transaction_type" label="Тип" width="130">
            <template #default="{ row }">
              <el-tag :type="row.transaction_type === 'ACCRUAL' ? 'warning' : 'success'">
                {{ row.transaction_type === 'ACCRUAL' ? 'Нарахування' : 'Виплата' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="category_name" label="Категорія" width="180" />
          <el-table-column label="Сума" width="150" align="right">
            <template #default="{ row }">
              <span :class="row.amount > 0 ? 'accrued-text' : 'paid-text'">
                {{ row.amount > 0 ? '+' : '' }}{{ formatCurrency(row.amount) }} ₴
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="Коментар" show-overflow-tooltip />
          <el-table-column prop="creator_name" label="Хто вніс" width="150" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- ACCRUAL/PAYMENT DIALOG -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingTrans.transaction_type === 'ACCRUAL' ? 'Нове нарахування' : 'Виплата зарплати'"
      width="500px"
    >
      <el-form :model="editingTrans" label-position="top" ref="formRef" :rules="rules">
        <el-form-item label="Співробітник" prop="employee_id">
          <el-select 
            v-model="editingTrans.employee_id" 
            placeholder="Оберіть співробітника" 
            filterable 
            style="width: 100%"
          >
            <el-option 
              v-for="emp in employeesList" 
              :key="emp.employee_id" 
              :label="emp.full_name" 
              :value="emp.employee_id" 
            />
          </el-select>
        </el-form-item>

        <div class="form-row">
          <el-form-item label="Дата" prop="date" style="flex: 1">
            <el-date-picker 
              v-model="editingTrans.date" 
              type="date" 
              placeholder="Оберіть дату" 
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="Сума (грн)" prop="amount" style="flex: 1">
            <el-input-number 
              v-model="editingTrans.amount" 
              :min="0" 
              :precision="2" 
              style="width: 100%"
            />
          </el-form-item>
        </div>

        <el-form-item 
          :label="editingTrans.transaction_type === 'ACCRUAL' ? 'Тип нарахування' : 'Метод виплати'" 
          prop="category_id"
        >
          <el-select v-model="editingTrans.category_id" placeholder="Оберіть категорію" style="width: 100%">
            <el-option 
              v-for="cat in (editingTrans.transaction_type === 'ACCRUAL' ? accrualTypes : paymentMethods)" 
              :key="cat.id" 
              :label="cat.name" 
              :value="cat.id" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Коментар" prop="description">
          <el-input 
            v-model="editingTrans.description" 
            type="textarea" 
            rows="3" 
            placeholder="За що нараховано / примітки до виплати"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="submitTransaction">
          Підтвердити
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, Wallet } from '@element-plus/icons-vue'
import api from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const activeTab = ref('balances')
const loading = ref(false)
const loadingHistory = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const searchQuery = ref('')
const historyRange = ref([])
const currentEmpFilter = ref(null)

const balances = ref([])
const history = ref([])
const accrualTypes = ref([])
const paymentMethods = ref([])

const editingTrans = ref({
  employee_id: '',
  amount: 0,
  transaction_type: 'ACCRUAL',
  date: new Date(),
  category_id: '',
  description: ''
})

const rules = {
  employee_id: [{ required: true, message: 'Оберіть співробітника', trigger: 'change' }],
  amount: [{ required: true, message: 'Вкажіть суму', trigger: 'blur' }],
  date: [{ required: true, message: 'Оберіть дату', trigger: 'change' }],
  category_id: [{ required: true, message: 'Оберіть категорію', trigger: 'change' }]
}

const employeesList = computed(() => balances.value)

const filteredBalances = computed(() => {
  if (!searchQuery.value) return balances.value
  const q = searchQuery.value.toLowerCase()
  return balances.value.filter(b => b.full_name.toLowerCase().includes(q))
})

const totalAccruedMonth = computed(() => {
  // Simplification for v2: sum of ALL balances. In real app would be filtered by month.
  return balances.value.reduce((acc, b) => acc + Number(b.total_accrued), 0)
})

const totalPaidMonth = computed(() => {
  return balances.value.reduce((acc, b) => acc + Number(b.total_paid), 0)
})

const totalBalance = computed(() => {
  return balances.value.reduce((acc, b) => acc + Number(b.balance), 0)
})

const fetchData = async () => {
  loading.value = true
  try {
    const [balRes, accRes, payRes] = await Promise.all([
      api.get('/api/v1/payroll/balance'),
      api.get('/api/v1/dictionaries/items?type=ACCRUAL_TYPE'),
      api.get('/api/v1/dictionaries/items?type=PAYMENT_METHOD')
    ])
    balances.value = balRes.data
    accrualTypes.value = accRes.data
    paymentMethods.value = payRes.data
  } catch (e) {
    ElMessage.error('Помилка завантаження балансу')
  } finally {
    loading.value = false
  }
}

const fetchHistory = async () => {
  loadingHistory.value = true
  try {
    const params = {}
    if (historyRange.value && historyRange.value.length === 2) {
      params.start_date = dayjs(historyRange.value[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(historyRange.value[1]).format('YYYY-MM-DD')
    }
    if (currentEmpFilter.value) {
      params.employee_id = currentEmpFilter.value
    }
    const res = await api.get('/api/v1/payroll/transactions', { params })
    
    // Supplement history with employee names from balances map
    const empMap = balances.value.reduce((m, b) => { m[b.employee_id] = b.full_name; return m }, {})
    history.value = res.data.map(h => ({
      ...h,
      employee_name: empMap[h.employee_id] || 'Невідомо'
    }))
  } catch (e) {
    ElMessage.error('Помилка завантаження історії')
  } finally {
    loadingHistory.value = false
  }
}

const handleNewTransaction = (type) => {
  editingTrans.value = {
    employee_id: '',
    amount: 0,
    transaction_type: type,
    date: new Date(),
    category_id: '',
    description: ''
  }
  dialogVisible.value = true
}

const viewHistory = (empId) => {
  currentEmpFilter.value = empId
  activeTab.value = 'history'
  fetchHistory()
}

const submitTransaction = async () => {
  submitting.value = true
  try {
    const payload = {
      ...editingTrans.value,
      date: dayjs(editingTrans.value.date).format('YYYY-MM-DD')
    }
    await api.post('/api/v1/payroll/transaction', payload)
    ElMessage.success('Транзакцію успішно додано')
    dialogVisible.value = false
    fetchData()
    if (activeTab.value === 'history') fetchHistory()
  } catch (e) {
    ElMessage.error('Помилка збереження транзакції')
  } finally {
    submitting.value = false
  }
}

const formatCurrency = (v) => Number(v || 0).toLocaleString('uk-UA', { minimumFractionDigits: 2 })

onMounted(() => {
  fetchData()
  fetchHistory()
})
</script>

<style scoped>
.payroll-manager {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.summary-card {
  border-radius: 12px;
}

.summary-card .value {
  font-size: 28px;
  font-weight: 700;
  text-align: center;
}

.summary-card.accrued .value { color: var(--el-color-warning); }
.summary-card.paid .value { color: var(--el-color-success); }
.summary-card.balance .value { color: var(--el-color-danger); }

.payroll-tabs {
  background: var(--el-bg-color);
  padding: 16px;
  border-radius: 12px;
  box-shadow: var(--el-box-shadow-light);
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.accrued-text {
  color: #f59e0b;
  font-weight: 600;
}

.paid-text {
  color: #10b981;
  font-weight: 600;
}

.form-row {
  display: flex;
  gap: 16px;
}
</style>
