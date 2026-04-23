<template>
  <div class="page-container">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" />
        <div class="name-section">
          <h2>{{ isEditMode ? form.name || 'Контрагент' : 'Новий контрагент' }}</h2>
          <div class="header-tags" v-if="isEditMode">
            <el-tag v-if="form.is_customer" type="success" size="small" round>Клієнт</el-tag>
            <el-tag v-if="form.is_supplier" type="warning" size="small" round>Постачальник</el-tag>
            <el-tag v-for="tag in (form.tags || [])" :key="tag" type="info" size="small" effect="plain" round>{{ tag }}</el-tag>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <template v-if="isEditMode">
          <el-button type="success" :icon="Plus" @click="createNewOrder">Нове замовлення</el-button>
          <el-button type="primary" @click="writeTelegram" plain>
            <el-icon><ChatDotRound /></el-icon> Telegram
          </el-button>
          <el-button type="info" @click="callPhone" plain>
            <el-icon><Phone /></el-icon> Зателефонувати
          </el-button>
        </template>
        
        <el-divider direction="vertical" />

        <el-button v-if="isEditMode" type="danger" @click="confirmDelete" plain>
          Видалити
        </el-button>
        <el-button @click="goBack">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveCounterparty">
          Зберегти
        </el-button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="editor-content" v-loading="loading">
      <el-tabs v-model="activeTab" class="cp-tabs">
        <!-- 1. General Information -->
        <el-tab-pane label="Загальна інформація" name="general">
          <div class="tab-content">
            <div class="form-grid">
              <!-- Left Column: Core and Supplier -->
              <div class="grid-col">
                <el-card shadow="never" class="form-card">
                  <template #header><span class="card-title">Основні дані</span></template>
                  <el-form :model="form" label-position="top" class="edit-form">
                    <el-form-item label="Назва (коротка)" required>
                      <el-input v-model="form.name" placeholder="Наприклад: ТОВ 'Атлант'" />
                    </el-form-item>
                    <el-form-item label="Юридична назва">
                      <el-input v-model="form.legal_name" placeholder="Повна юридична назва" />
                    </el-form-item>
                    <el-form-item label="ЄДРПОУ / ІПН">
                      <el-input v-model="form.tax_id" placeholder="8 або 10 цифр" />
                    </el-form-item>
                    <div class="flags-box">
                      <el-form-item label="Це клієнт?">
                        <el-switch v-model="form.is_customer" />
                      </el-form-item>
                      <el-form-item label="Це постачальник?">
                        <el-switch v-model="form.is_supplier" />
                      </el-form-item>
                      <el-form-item label="Активний?">
                        <el-switch v-model="form.is_active" />
                      </el-form-item>
                    </div>
                  </el-form>
                </el-card>

                <!-- Supplier Block -->
                <el-card v-if="form.is_supplier" shadow="never" class="form-card mt-20">
                  <template #header><span class="card-title">Налаштування постачальника</span></template>
                  <el-form :model="form" label-position="top" class="edit-form">
                    <div class="form-row">
                      <el-form-item label="Час доставки (днів)" class="flex-1">
                        <el-input-number v-model="form.delivery_days" :min="0" class="w-full" />
                      </el-form-item>
                      <el-form-item label="Мін. замовлення (грн)" class="flex-1">
                        <el-input-number v-model="form.min_order_amount" :min="0" class="w-full" />
                      </el-form-item>
                    </div>
                    <el-form-item label="Умови оплати">
                      <el-select v-model="form.payment_terms_id" placeholder="Оберіть умови..." class="w-full" clearable>
                        <el-option v-for="p in paymentTerms" :key="p.id" :label="p.name" :value="p.id" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="Контактна особа">
                      <el-input v-model="form.contact_person" placeholder="ПІБ контактної особи" />
                    </el-form-item>
                    <el-form-item label="Матеріали">
                      <el-input v-model="form.supplied_materials" type="textarea" :rows="2" placeholder="Що постачає..." />
                    </el-form-item>
                  </el-form>
                </el-card>
              </div>

              <!-- Right Column: CRM and Logistics -->
              <div class="grid-col">
                <el-card shadow="never" class="form-card">
                  <template #header><span class="card-title">Контакти та CRM</span></template>
                  <el-form :model="form" label-position="top" class="edit-form">
                    <div class="form-row">
                      <el-form-item label="Телефон" class="flex-1">
                        <el-input v-model="form.phone" placeholder="+380...">
                          <template #prefix><el-icon><Phone /></el-icon></template>
                        </el-input>
                      </el-form-item>
                      <el-form-item label="Email" class="flex-1">
                        <el-input v-model="form.email" placeholder="example@mail.com">
                          <template #prefix><el-icon><Message /></el-icon></template>
                        </el-input>
                      </el-form-item>
                    </div>
                    
                    <template v-if="form.is_customer">
                      <el-form-item label="Канал звернення">
                        <el-select v-model="form.acquisition_channel_id" placeholder="Оберіть канал..." class="w-full" clearable>
                          <el-option v-for="c in channels" :key="c.id" :label="c.name" :value="c.id" />
                        </el-select>
                      </el-form-item>
                      <div class="form-row">
                        <el-form-item label="Місто" class="flex-1">
                          <el-input v-model="form.city" placeholder="Місто..." />
                        </el-form-item>
                        <el-form-item label="Відділення НП" class="flex-1">
                          <el-input v-model="form.np_department" placeholder="Відділення..." />
                        </el-form-item>
                      </div>
                      <el-form-item label="Знижка %">
                        <el-input-number v-model="form.discount_percent" :min="0" :max="100" class="w-full" />
                      </el-form-item>
                      <el-form-item label="Теги">
                        <el-select v-model="form.tags" multiple filterable allow-create default-first-option placeholder="Теги клієнта" class="w-full">
                          <el-option v-for="t in tagOptions" :key="t.id" :label="t.name" :value="t.name" />
                        </el-select>
                      </el-form-item>
                    </template>

                    <el-form-item label="Нотатки">
                      <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="Додаткова інформація..." />
                    </el-form-item>
                  </el-form>
                </el-card>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 2. Sales History -->
        <el-tab-pane v-if="form.is_customer" label="Історія продажів" name="sales" :disabled="!isEditMode">
          <div class="tab-content">
            <el-card shadow="never" class="form-card">
              <template #header>
                <div class="card-header-flex">
                  <span class="card-title">Замовлення</span>
                  <el-button type="primary" size="small" :icon="Plus" @click="createNewOrder" plain>Нове замовлення</el-button>
                </div>
              </template>
              <el-table :data="salesOrders" style="width: 100%">
                <el-table-column prop="order_number" label="Номер" width="120" />
                <el-table-column label="Дата" width="120">
                  <template #default="{ row }">{{ formatDate(row.order_date) }}</template>
                </el-table-column>
                <el-table-column label="Виріб" min-width="200">
                  <template #default="{ row }">
                    <span class="product-info">{{ row.product_summary || '—' }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="Статус" width="130">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small" effect="dark" class="u-status">
                      {{ getStatusLabel(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Оплата" width="120">
                  <template #default="{ row }">
                    <el-tag :type="row.payment_status === 'paid' ? 'success' : 'info'" size="small" plain>
                      {{ row.payment_status === 'paid' ? 'Оплачено' : 'Не оплачено' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Сума" width="130" align="right">
                  <temp        <!-- 3. Purchase History -->
        <el-tab-pane v-if="form.is_supplier" label="Історія закупівель" name="purchases" :disabled="!isEditMode">
          <div class="tab-content">
            <el-card shadow="never" class="form-card">
              <template #header><span class="card-title">Прибуткові накладні</span></template>
              <el-table :data="purchaseReceipts" style="width: 100%">
                <el-table-column prop="receipt_number" label="Номер" width="140" />
                <el-table-column label="Дата" width="120">
                  <template #default="{ row }">{{ formatDate(row.receipt_date) }}</template>
                </el-table-column>
                <el-table-column label="Статус" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small" effect="dark">
                      {{ getStatusLabel(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Сума" width="150" align="right">
                  <template #default="{ row }">
                    <strong>{{ formatCurrency(row.total_amount) }}</strong>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="purchaseReceipts.length === 0" description="Немає накладних" />
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 4. Bank Accounts (Реквізити) -->
        <el-tab-pane label="Реквізити" name="bank_accounts" :disabled="!isEditMode">
          <div class="tab-content">
            <el-card shadow="never" class="form-card">
              <template #header>
                <div class="card-header-flex">
                  <span class="card-title">Банківські рахунки</span>
                  <el-button type="primary" size="small" :icon="Plus" @click="openAccountDialog" plain>Додати рахунок</el-button>
                </div>
              </template>
              <el-table :data="form.bank_accounts" style="width: 100%">
                <el-table-column prop="bank_name" label="Банк" width="180" />
                <el-table-column prop="iban" label="IBAN" min-width="250" />
                <el-table-column prop="currency" label="Валюта" width="100" />
                <el-table-column prop="purpose" label="Призначення" />
                <el-table-column label="Статус" width="100" align="center">
                  <template #default="{ row }">
                    <el-icon v-if="row.is_active" color="#48bb78"><CircleCheckFilled /></el-icon>
                    <el-icon v-else color="#cbd5e0"><CircleCloseFilled /></el-icon>
                  </template>
                </el-table-column>
                <el-table-column width="60" align="right">
                  <template #default="{ row }">
                    <el-button type="danger" :icon="Delete" circle size="small" @click="removeAccount(row.id)" plain />
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!form.bank_accounts?.length" description="Рахунків не додано" />
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 5. Materials (for Suppliers) -->
        <el-tab-pane v-if="form.is_supplier" label="Матеріали" name="materials" :disabled="!isEditMode">
          <div class="tab-content">
            <el-card shadow="never" class="form-card">
              <template #header>
                <div class="card-header-flex">
                  <span class="card-title">Матеріали що постачає</span>
                  <el-button type="primary" size="small" :icon="Plus" @click="openMaterialDialog" plain>Додати матеріал</el-button>
                </div>
              </template>
              <el-table :data="form.materials" style="width: 100%">
                <el-table-column prop="product_name" label="Назва матеріалу" min-width="200" />
                <el-table-column label="Ціна" width="180" align="right">
                  <template #default="{ row }">
                    <strong>{{ formatCurrency(row.price) }}</strong>
                  </template>
                </el-table-column>
                <el-table-column prop="currency" label="Валюта" width="100" />
                <el-table-column width="60" align="right">
                  <template #default="{ row }">
                    <el-button type="danger" :icon="Delete" circle size="small" @click="removeMaterial(row.id)" plain />
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!form.materials?.length" description="Матеріалів не додано" />
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 6. Contacts -->
        <el-tab-pane label="Контакти" name="contacts" :disabled="!isEditMode">
          <div class="tab-content">
            <el-card shadow="never" class="form-card">
              <template #header>
                <div class="card-header-flex">
                  <span class="card-title">Контактні особи</span>
                  <el-button type="primary" size="small" :icon="Plus" @click="openContactDialog" plain>Додати контакт</el-button>
                </div>
              </template>
              <el-table :data="form.contacts" style="width: 100%">
                <el-table-column prop="name" label="Ім'я" min-width="180">
                  <template #default="{ row }">
                    {{ row.name }} <el-tag v-if="row.is_primary" size="small" type="success" effect="plain" round>Основний</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="position" label="Посада" width="150" />
                <el-table-column prop="phone" label="Телефон" width="150" />
                <el-table-column prop="telegram" label="Telegram" width="140" />
                <el-table-column prop="email" label="Email" min-width="180" />
                <el-table-column width="60" align="right">
                  <template #default="{ row }">
                    <el-button type="danger" :icon="Delete" circle size="small" @click="removeContact(row.id)" plain />
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!form.contacts?.length" description="Контактів не додано" />
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 7. Finances -->
        <el-tab-pane label="Фінанси" name="finances" :disabled="!isEditMode">
atusLabel(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Сума" width="150" align="right">
                  <template #default="{ row }">
                    <strong>{{ formatCurrency(row.total_amount) }}</strong>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="purchaseReceipts.length === 0" description="Немає накладних" />
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 4. Finances -->
        <el-tab-pane label="Фінанси" name="finances" :disabled="!isEditMode">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card shadow="never" class="finance-card">
                  <div class="f-stat">
                    <span class="f-label">Всього продажів</span>
                    <span class="f-value text-success">{{ formatCurrency(financeSummary.totalSales) }}</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card shadow="never" class="finance-card">
                  <div class="f-stat">
                    <span class="f-label">Всього закупівель</span>
                    <span class="f-value text-warning">{{ formatCurrency(financeSummary.totalPurchases) }}</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card shadow="never" class="finance-card">
                  <div class="f-stat">
                    <span class="f-label">Баланс (Сальдо)</span>
                    <span class="f-value" :class="financeSummary.balance >= 0 ? 'text-success' : 'text-danger'">
                      {{ formatCurrency(financeSummary.balance) }}
                    </span>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <el-card shadow="never" class="form-card mt-20">
              <template #header><span class="card-title">Фінансові операції</span></template>
              <el-table :data="financeOperations" style="width: 100%">
                <el-table-column label="Дата" width="120">
                  <template #default="{ row }">{{ formatDate(row.date) }}</template>
                </el-table-column>
                <el-table-column prop="reference" label="Документ" width="140" />
                <el-table-column prop="type" label="Тип" width="160">
                  <template #default="{ row }">
                    <el-tag :type="row.type.includes('Продаж') ? 'success' : 'warning'" size="small" plain>{{ row.type }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Сума" width="150" align="right">
                  <template #default="{ row }">
                    <strong :class="row.amount < 0 ? 'text-danger' : 'text-success'">
                      {{ formatCurrency(row.amount) }}
                    </strong>
                  </template>
                </el-table-column>
                <el-table-column label="Оплата">
                  <template #default="{ row }">
                    <el-tag :type="row.is_paid ? 'success' : 'danger'" size="small">
                      {{ row.is_paid ? 'Оплачено' : 'Очікується' }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- DIALOGS -->
      <!-- Bank Account Dialog -->
      <el-dialog v-model="accountDialog.visible" title="Додати банківський рахунок" width="450px">
        <el-form :model="accountDialog.form" label-position="top">
          <el-form-item label="Назва банку">
            <el-input v-model="accountDialog.form.bank_name" placeholder="Наприклад: ПриватБанк" />
          </el-form-item>
          <el-form-item label="IBAN" required>
            <el-input v-model="accountDialog.form.iban" placeholder="UA..." />
          </el-form-item>
          <div class="form-row">
            <el-form-item label="Валюта" class="flex-1">
              <el-select v-model="accountDialog.form.currency">
                <el-option label="Гривня (UAH)" value="UAH" />
                <el-option label="Долар (USD)" value="USD" />
                <el-option label="Євро (EUR)" value="EUR" />
              </el-select>
            </el-form-item>
            <el-form-item label="Активний" class="flex-1">
              <el-switch v-model="accountDialog.form.is_active" />
            </el-form-item>
          </div>
          <el-form-item label="Призначення">
            <el-input v-model="accountDialog.form.purpose" placeholder="Наприклад: Основний для оплат" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="accountDialog.visible = false">Скасувати</el-button>
          <el-button type="primary" @click="saveBankAccount" :loading="accountDialog.loading">Зберегти</el-button>
        </template>
      </el-dialog>

      <!-- Material Dialog -->
      <el-dialog v-model="materialDialog.visible" title="Додати матеріал постачальника" width="500px">
        <el-form :model="materialDialog.form" label-position="top">
          <el-form-item label="Виберіть товар/матеріал з каталогу" required>
            <el-select v-model="materialDialog.form.product_id" filterable remote :remote-method="searchProducts" :loading="materialDialog.searchLoading" placeholder="Почніть вводити назву..." class="w-full">
              <el-option v-for="p in productResults" :key="p.id" :label="`${p.name} (${p.sku})`" :value="p.id" />
            </el-select>
          </el-form-item>
          <div class="form-row">
            <el-form-item label="Ціна постачальника" class="flex-1">
              <el-input-number v-model="materialDialog.form.price" :min="0" class="w-full" />
            </el-form-item>
            <el-form-item label="Валюта" class="flex-1">
              <el-select v-model="materialDialog.form.currency">
                <el-option label="UAH" value="UAH" />
                <el-option label="USD" value="USD" />
                <el-option label="EUR" value="EUR" />
              </el-select>
            </el-form-item>
          </div>
        </el-form>
        <template #footer>
          <el-button @click="materialDialog.visible = false">Скасувати</el-button>
          <el-button type="primary" @click="saveMaterial" :loading="materialDialog.loading">Додати</el-button>
        </template>
      </el-dialog>

      <!-- Contact Dialog -->
      <el-dialog v-model="contactDialog.visible" title="Додати контактну особу" width="450px">
        <el-form :model="contactDialog.form" label-position="top">
          <el-form-item label="ПІБ" required>
            <el-input v-model="contactDialog.form.name" placeholder="Іван Іванов" />
          </el-form-item>
          <el-form-item label="Посада">
            <el-input v-model="contactDialog.form.position" placeholder="Менеджер..." />
          </el-form-item>
          <div class="form-row">
            <el-form-item label="Телефон" class="flex-1">
              <el-input v-model="contactDialog.form.phone" />
            </el-form-item>
            <el-form-item label="Email" class="flex-1">
              <el-input v-model="contactDialog.form.email" />
            </el-form-item>
          </div>
          <div class="form-row">
            <el-form-item label="Telegram" class="flex-1">
              <el-input v-model="contactDialog.form.telegram" placeholder="@username" />
            </el-form-item>
            <el-form-item label="Основний контакт" class="flex-1">
              <el-switch v-model="contactDialog.form.is_primary" />
            </el-form-item>
          </div>
        </el-form>
        <template #footer>
          <el-button @click="contactDialog.visible = false">Скасувати</el-button>
          <el-button type="primary" @click="saveContact" :loading="contactDialog.loading">Зберегти</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ArrowLeft, Phone, Message, Document, 
  ChatDotRound, Plus, Right, Delete,
  CircleCheckFilled, CircleCloseFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const route = useRoute()
const router = useRouter()

// State
const activeTab = ref('general')
const submitting = ref(false)
const loading = ref(false)
const isEditMode = computed(() => !!route.params.id)

// Dictionary Data
const channels = ref([])
const tagOptions = ref([])

const form = reactive({
  id: null,
  name: '',
  legal_name: '',
  tax_id: '',
  is_customer: true,
  is_supplier: false,
  phone: '',
  email: '',
  address: '',
  default_contract: '',
  is_active: true,
  acquisition_channel_id: null,
  city: '',
  np_department: '',
  discount_percent: 0,
  notes: '',
  tags: [],
  delivery_days: 0,
  min_order_amount: 0,
  payment_terms_id: null,
  payment_terms: '',
  contact_person: '',
  supplied_materials: '',
  bank_accounts: [],
  contacts: [],
  materials: []
})

// Dialog States
const accountDialog = reactive({
  visible: false, loading: false,
  form: { bank_name: '', iban: '', currency: 'UAH', purpose: '', is_active: true }
})

const materialDialog = reactive({
  visible: false, loading: false, searchLoading: false,
  form: { product_id: null, price: 0, currency: 'UAH' }
})

const contactDialog = reactive({
  visible: false, loading: false,
  form: { name: '', position: '', phone: '', telegram: '', email: '', is_primary: false }
})

const productResults = ref([])
const paymentTerms = ref([])

const salesOrders = ref([])
const purchaseReceipts = ref([])
const financeSummary = reactive({
  totalSales: 0,
  totalPurchases: 0,
  balance: 0
})

const financeOperations = computed(() => {
  const ops = []
  salesOrders.value.forEach(o => ops.push({
    id: o.id, date: o.order_date, reference: o.order_number, 
    type: 'Замовлення (Продаж)', amount: Number(o.total_amount), 
    is_paid: o.payment_status === 'paid', sort_date: new Date(o.order_date)
  }))
  purchaseReceipts.value.forEach(r => ops.push({
    id: r.id, date: r.receipt_date, reference: r.receipt_number, 
    type: 'Прибуткова накладна', amount: -Number(r.total_amount), 
    is_paid: r.status === 'done', sort_date: new Date(r.receipt_date)
  }))
  return ops.sort((a, b) => b.sort_date - a.sort_date)
})

// Methods
const goBack = () => router.push('/sales/counterparties')

const fetchCounterparty = async () => {
  if (!isEditMode.value) return
  loading.value = true
  try {
    const res = await api.get(`/api/v1/counterparties/${route.params.id}`)
    Object.assign(form, res.data)
    if (!form.tags) form.tags = []
    fetchSalesHistory()
    fetchPurchaseHistory()
  } catch (e) {
    ElMessage.error('Помилка завантаження')
  } finally {
    loading.value = false
  }
}

const fetchDictionaries = async () => {
  try {
    const [cRes, tRes, pRes] = await Promise.all([
      api.get('/api/v1/dictionaries/LEAD_SOURCE'),
      api.get('/api/v1/dictionaries/CLIENT_TAG'),
      api.get('/api/v1/dictionaries/PAYMENT_TERMS')
    ])
    channels.value = cRes.data || []
    tagOptions.value = tRes.data || []
    paymentTerms.value = pRes.data || []
  } catch (e) {}
}

const fetchSalesHistory = async () => {
  try {
    const res = await api.get('/api/v1/orders', { params: { counterparty_id: route.params.id } })
    salesOrders.value = res.data || []
    calculateFinance()
  } catch (e) {}
}

const fetchPurchaseHistory = async () => {
  try {
    const res = await api.get('/api/v1/purchase-receipts', { params: { supplier_id: route.params.id } })
    purchaseReceipts.value = res.data || []
    calculateFinance()
  } catch (e) {}
}

const calculateFinance = () => {
  financeSummary.totalSales = salesOrders.value.reduce((acc, o) => acc + Number(o.total_amount), 0)
  financeSummary.totalPurchases = purchaseReceipts.value.reduce((acc, r) => acc + Number(r.total_amount), 0)
  financeSummary.balance = financeSummary.totalSales - financeSummary.totalPurchases
}

const saveCounterparty = async () => {
  if (!form.name) return ElMessage.warning('Вкажіть назву')
  submitting.value = true
  try {
    // Clean up lists before saving main form
    const { bank_accounts, contacts, materials, documents, ...payload } = form
    if (isEditMode.value) {
      await api.put(`/api/v1/counterparties/${form.id}`, payload)
      ElMessage.success('Оновлено')
    } else {
      const res = await api.post('/api/v1/counterparties', payload)
      ElMessage.success('Створено')
      router.push(`/sales/counterparties/${res.data.id}`)
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Помилка')
  } finally {
    submitting.value = false
  }
}

// --- Bank Account Methods ---
const openAccountDialog = () => {
  accountDialog.form = { bank_name: '', iban: '', currency: 'UAH', purpose: '', is_active: true }
  accountDialog.visible = true
}

const saveBankAccount = async () => {
  if (!accountDialog.form.iban) return ElMessage.warning('Вкажіть IBAN')
  accountDialog.loading = true
  try {
    await api.post(`/api/v1/counterparties/${form.id}/bank-accounts`, accountDialog.form)
    ElMessage.success('Рахунок додано')
    accountDialog.visible = false
    fetchCounterparty()
  } catch (e) {
    ElMessage.error('Помилка збереження рахунку')
  } finally {
    accountDialog.loading = false
  }
}

const removeAccount = async (accId) => {
  try {
    await ElMessageBox.confirm('Видалити цей рахунок?', 'Увага', { type: 'warning' })
    await api.delete(`/api/v1/counterparties/${form.id}/bank-accounts/${accId}`)
    fetchCounterparty()
  } catch (e) {}
}

// --- Contact Methods ---
const openContactDialog = () => {
  contactDialog.form = { name: '', position: '', phone: '', telegram: '', email: '', is_primary: false }
  contactDialog.visible = true
}

const saveContact = async () => {
  if (!contactDialog.form.name) return ElMessage.warning('Вкажіть ім\'я')
  contactDialog.loading = true
  try {
    await api.post(`/api/v1/counterparties/${form.id}/contacts`, contactDialog.form)
    ElMessage.success('Контакт додано')
    contactDialog.visible = false
    fetchCounterparty()
  } catch (e) {
    ElMessage.error('Помилка збереження контакту')
  } finally {
    contactDialog.loading = false
  }
}

const removeContact = async (cId) => {
  try {
    await ElMessageBox.confirm('Видалити цей контакт?', 'Увага', { type: 'warning' })
    await api.delete(`/api/v1/counterparties/${form.id}/contacts/${cId}`)
    fetchCounterparty()
  } catch (e) {}
}

// --- Material Methods ---
const openMaterialDialog = () => {
  materialDialog.form = { product_id: null, price: 0, currency: 'UAH' }
  materialDialog.visible = true
}

const searchProducts = async (query) => {
  if (query.length < 2) return
  materialDialog.searchLoading = true
  try {
    const res = await api.get('/api/v1/products', { params: { search: query, limit: 10 } })
    productResults.value = res.data || []
  } catch (e) {} finally {
    materialDialog.searchLoading = false
  }
}

const saveMaterial = async () => {
  if (!materialDialog.form.product_id) return ElMessage.warning('Оберіть матеріал')
  materialDialog.loading = true
  try {
    await api.post(`/api/v1/counterparties/${form.id}/materials`, materialDialog.form)
    ElMessage.success('Матеріал додано')
    materialDialog.visible = false
    fetchCounterparty()
  } catch (e) {
    ElMessage.error('Помилка додавання матеріалу')
  } finally {
    materialDialog.loading = false
  }
}

const removeMaterial = async (mId) => {
  try {
    await ElMessageBox.confirm('Видалити цей матеріал?', 'Увага', { type: 'warning' })
    await api.delete(`/api/v1/counterparties/${form.id}/materials/${mId}`)
    fetchCounterparty()
  } catch (e) {}
}

const confirmDelete = async () => {
  try {
    await ElMessageBox.confirm('Видалити цього контрагента?', 'Увага', { type: 'warning' })
    await api.delete(`/api/v1/counterparties/${form.id}`)
    ElMessage.success('Видалено')
    goBack()
  } catch (e) {}
}

const writeTelegram = () => {
  if (!form.phone) return ElMessage.info('Вкажіть телефон')
  window.open(`https://t.me/${form.phone.replace(/\D/g, '')}`, '_blank')
}

const callPhone = () => {
  if (!form.phone) return ElMessage.info('Вкажіть телефон')
  window.location.href = `tel:${form.phone}`
}

const createNewOrder = () => router.push({ name: 'OrderEditor', query: { counterparty_id: form.id } })
const viewOrder = (order) => router.push(`/sales/orders/${order.id}`)

const formatDate = (d) => d ? new Date(d).toLocaleDateString('uk-UA') : '—'
const formatCurrency = (v) => new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(v || 0)

const getStatusLabel = (s) => ({
  'draft': 'ЧЕРНЕТКА', 'confirmed': 'ПІДТВЕРДЖЕНО', 'in_production': 'В РОБОТІ',
  'done': 'ГОТОВО', 'cancelled': 'СКАСОВАНО', 'shipped': 'ВІДВАНТАЖЕНО'
}[s] || s)

const getStatusType = (s) => ({
  'draft': 'info', 'confirmed': 'primary', 'in_production': 'warning',
  'done': 'success', 'shipped': 'success', 'cancelled': 'danger'
}[s] || 'info')

onMounted(() => {
  fetchDictionaries()
  fetchCounterparty()
})
</script>

<style scoped>
.page-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  padding: 15px 25px;
  background: white;
  border-bottom: 1px solid #edf2f7;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left { display: flex; align-items: center; gap: 15px; }
.name-section h2 { margin: 0; font-size: 20px; color: #1a202c; }
.header-tags { display: flex; gap: 6px; margin-top: 4px; }
.header-actions { display: flex; align-items: center; gap: 10px; }

.editor-content { flex: 1; overflow-y: auto; background: #f7fafc; }
.tab-content { padding: 25px; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
.form-card { border-radius: 12px; border: none; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
.card-title { font-weight: 700; color: #2d3748; }

.flags-box {
  display: flex; justify-content: space-between;
  background: #f8fafc; padding: 15px; border-radius: 8px; margin-top: 15px;
}

.mt-20 { margin-top: 20px; }
.w-full { width: 100%; }
.flex-1 { flex: 1; }
.form-row { display: flex; gap: 15px; }
.card-header-flex { display: flex; justify-content: space-between; align-items: center; }

.finance-card { border-radius: 12px; text-align: center; }
.f-stat { padding: 10px; }
.f-label { display: block; font-size: 12px; color: #718096; margin-bottom: 5px; }
.f-value { font-size: 20px; font-weight: 800; }

.text-success { color: #48bb78; }
.text-warning { color: #ed8936; }
.text-danger { color: #f56565; }

.u-status { font-weight: 700; letter-spacing: 0.5px; }
.product-info { font-size: 13px; color: #4a5568; }

@media (max-width: 1024px) {
  .form-grid { grid-template-columns: 1fr; }
}
</style>
