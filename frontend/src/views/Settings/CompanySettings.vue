<template>
  <div class="company-settings-page">
    <div class="page-header">
      <div class="header-content">
        <h1>Керування організаціями</h1>
        <p class="subtitle">Налаштування юридичних осіб (ФОП/ТОВ) та податкових ставок</p>
      </div>
      <div class="header-actions">
        <el-button type="success" @click="createNewCompany">
          <el-icon class="mr-2"><Plus /></el-icon> Додати організацію
        </el-button>
        <el-button type="primary" :loading="saving" @click="saveSettings" v-if="selectedCompany">
          <el-icon class="mr-2"><Check /></el-icon> Зберегти зміни
        </el-button>
      </div>
    </div>

    <!-- ORGANIZATIONS LIST -->
    <div class="companies-grid mb-6">
       <el-card 
         v-for="company in companies" 
         :key="company.id" 
         :class="['company-card', { active: selectedCompany?.id === company.id }]"
         @click="selectCompany(company)"
       >
         <div class="card-status">
            <el-tag v-if="company.is_default" type="success" effect="dark" size="small">Основна</el-tag>
         </div>
         <div class="card-body">
            <h3>{{ company.name }}</h3>
            <p class="type-tag">{{ company.company_type }} • {{ company.tax_group }}</p>
            <p class="edrpou">ЄДРПОУ: {{ company.edrpou }}</p>
         </div>
         <div class="card-footer">
            <el-button v-if="!company.is_default" size="small" link @click.stop="makeDefault(company.id)">Зробити основною</el-button>
         </div>
       </el-card>
    </div>

    <el-card class="settings-card" v-loading="loading" v-if="selectedCompany">
      <el-tabs v-model="activeTab" class="settings-tabs">
        
        <!-- MAIN INFO TAB -->
        <el-tab-pane label="Основна інформація" name="general" lazy>
          <el-form label-position="top" class="settings-form">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="Тип організації">
                  <el-radio-group v-model="form.company_type" @change="handleTypeChange">
                    <el-radio-button value="FOP">ФОП</el-radio-button>
                    <el-radio-button value="TOV">Юридична особа (ТОВ, ПП)</el-radio-button>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="12" v-if="form.company_type === 'FOP'">
                 <el-alert
                    title="Для ФОП доступні спрощені налаштування"
                    type="info"
                    show-icon
                    :closable="false"
                  />
              </el-col>
            </el-row>
            
            <el-divider content-position="left">Назва</el-divider>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="Коротка назва (для відображення)">
                  <el-input v-model="form.name" placeholder="Напр. ФОП Петренко" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Повна юридична назва">
                   <el-input v-model="form.full_name_uk" placeholder="Напр. Фізична особа-підприємець Петренко Петро Петрович" />
                </el-form-item>
              </el-col>
            </el-row>

             <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="Назва англійською (для ЗЕД)">
                  <el-input v-model="form.full_name_en" placeholder="e.g. FOP Petrenko P.P." />
                </el-form-item>
              </el-col>
               <el-col :span="12">
                <el-form-item label="Веб-сайт">
                  <el-input v-model="form.website" placeholder="https://..." />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">Контакти</el-divider>
            <el-row :gutter="24">
               <el-col :span="8">
                <el-form-item label="Email">
                  <el-input v-model="form.email" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Телефон">
                  <el-input v-model="form.phone" />
                </el-form-item>
              </el-col>
            </el-row>

          </el-form>
        </el-tab-pane>

        <!-- LEGAL DETAILS TAB -->
        <el-tab-pane label="Реквізити та Адреси" name="details" lazy>
          <el-form label-position="top" class="settings-form">
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item :label="form.company_type === 'FOP' ? 'РНОКПП (ІПН)' : 'ЄДРПОУ'">
                   <div class="flex gap-2">
                      <el-input v-model="form.edrpou" placeholder="Введіть код" />
                      <el-button type="warning" plain @click="autofillByEdrpou" :loading="autofillLoading">
                        <el-icon class="mr-1"><MagicStick /></el-icon> Автозаповнення
                      </el-button>
                   </div>
                </el-form-item>
              </el-col>
               <el-col :span="12">
                 <el-form-item label="Основний КВЕД">
                    <el-input v-model="form.kved" placeholder="Напр. 62.01" />
                 </el-form-item>
               </el-col>
            </el-row>

            <el-divider content-position="left">Підписанти</el-divider>
            <el-row :gutter="24">
               <el-col :span="12">
                 <el-form-item label="ПІБ Керівника (Директора)">
                    <el-input v-model="form.director_name" />
                 </el-form-item>
               </el-col> 
               <el-col :span="12">
                 <el-form-item label="Посада керівника">
                    <el-input v-model="form.director_position" placeholder="Директор / Генеральний директор" />
                 </el-form-item>
               </el-col>
            </el-row>

             <el-divider content-position="left">Адреси</el-divider>
             <el-row :gutter="24">
               <el-col :span="12">
                 <el-form-item label="Юридична адреса">
                    <el-input v-model="form.legal_address" type="textarea" :rows="2" />
                 </el-form-item>
               </el-col>
                <el-col :span="12">
                 <el-form-item label="Фактична адреса">
                    <el-input v-model="form.physical_address" type="textarea" :rows="2" />
                    <el-checkbox v-model="sameAddress" @change="handleSameAddress">Співпадає з юридичною</el-checkbox>
                 </el-form-item>
               </el-col>
             </el-row>

          </el-form>
        </el-tab-pane>

        <!-- TAXATION TAB -->
        <el-tab-pane label="Оподаткування" name="tax" lazy>
           <el-row :gutter="24">
             <el-col :span="14">
                <el-form label-position="top" class="settings-form">
                  <div class="form-section-title">⚖️ Налаштування системи</div>
                  <el-form-item label="Система оподаткування">
                      <el-select v-model="form.tax_group" placeholder="Оберіть групу" @change="saveSettings">
                        <el-option label="1 група (ФОП)" value="GROUP_1" />
                        <el-option label="2 група (ФОП)" value="GROUP_2" />
                        <el-option label="3 група (ФОП/ТОВ) - 5%" value="GROUP_3" />
                        <el-option label="Загальна система" value="GENERAL" />
                      </el-select>
                  </el-form-item>

                  <el-form-item>
                    <el-checkbox v-model="form.vat_payer" border @change="saveSettings">Платник ПДВ</el-checkbox>
                  </el-form-item>

                  <div class="form-section-title mt-6">📊 Базові показники ({{ taxSettings.tax_year }})</div>
                  <el-row :gutter="12">
                    <el-col :span="12">
                      <el-form-item label="Мінімальна зарплата (МЗП)">
                        <el-input-number v-model="taxSettings.min_wage" :min="0" style="width: 100%" @change="saveSettings" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="Прожитковий мінімум (ПМ)">
                        <el-input-number v-model="taxSettings.subsistence_min" :min="0" style="width: 100%" @change="saveSettings" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <div class="tax-limit-info mt-4 p-4 bg-gray-50 rounded">
                    <div class="flex justify-between items-center mb-2">
                       <span class="text-gray-600">Ліміт доходу на рік:</span>
                       <strong class="text-lg">{{ formatCurrency(incomeLimit) }} грн</strong>
                    </div>
                    <div class="text-xs text-gray-400">Формула: {{ taxSettings.min_wage }} × {{ form.tax_group === 'GROUP_1' ? taxSettings.limit_multiplier_g1 : (form.tax_group === 'GROUP_2' ? taxSettings.limit_multiplier_g2 : taxSettings.limit_multiplier_g3) }}</div>
                  </div>

                  <div class="form-section-title mt-6">💸 Щомісячні платежі</div>
                  <div class="monthly-payments-card">
                     <div class="payment-item">
                        <span class="label">ЄСВ (22% × МЗП):</span>
                        <span class="value">{{ formatCurrency(monthlyESV) }} грн</span>
                     </div>
                     <div class="payment-item">
                        <span class="label">Єдиний податок ({{ form.tax_group === 'GROUP_1' ? '10% × ПМ' : '20% × МЗП' }}):</span>
                        <span class="value" v-if="form.tax_group !== 'GROUP_3'">{{ formatCurrency(monthlySingleTax) }} грн</span>
                        <span class="value text-blue-500" v-else>5% від доходу</span>
                     </div>
                     <div class="payment-item">
                        <span class="label">Військовий збір ({{ form.tax_group === 'GROUP_3' ? '1% від доходу' : '10% × МЗП' }}):</span>
                        <span class="value" v-if="form.tax_group !== 'GROUP_3'">{{ formatCurrency(monthlyMilitary) }} грн</span>
                        <span class="value text-blue-500" v-else>1% від доходу</span>
                     </div>
                     <el-divider />
                     <div class="payment-item total">
                        <span class="label">РАЗОМ на місяць:</span>
                        <span class="value">{{ formatCurrency(monthlyTotal) }} грн</span>
                     </div>
                  </div>
                </el-form>

                <!-- FOP INCOME WIDGET (Previous logic maintained) -->
                <div class="income-widget mt-8" v-if="incomeData">
                  <div class="widget-header">
                    <h4>💳 Дохід ФОП за {{ taxSettings.tax_year }} рік</h4>
                    <span class="total-amount">{{ formatCurrency(incomeData.total) }} грн</span>
                  </div>
                  
                  <div class="progress-section">
                    <div class="progress-labels">
                      <span>Прогрес до ліміту</span>
                      <span>{{ ((incomeData.total / incomeLimit) * 100).toFixed(1) }}%</span>
                    </div>
                    <el-progress 
                      :percentage="Math.min((incomeData.total / incomeLimit) * 100, 100)" 
                      :status="getProgressStatus((incomeData.total / incomeLimit) * 100)"
                      :stroke-width="12"
                      :show-text="false"
                    />
                    <div class="progress-footer">
                      <span>Залишок: <strong>{{ formatCurrency(incomeLimit - incomeData.total) }} грн</strong></span>
                      <span>Ліміт: {{ formatCurrency(incomeLimit) }} грн</span>
                    </div>
                  </div>

                  <div class="quarters-grid mt-4">
                    <div v-for="(q, idx) in incomeData.quarters" :key="idx" class="q-item">
                      <span class="q-name">Q{{ idx + 1 }}</span>
                      <span class="q-val">{{ formatCurrency(q) }}</span>
                    </div>
                  </div>
                </div>
             </el-col>

             <el-col :span="10">
                <div class="tax-calendar-widget mb-6">
                   <h4>📅 Податковий календар</h4>
                   <div class="calendar-list">
                      <div v-for="(event, idx) in calendarEvents" :key="idx" class="calendar-item">
                         <div class="event-date">
                            <span class="day">{{ event.date.split('-')[2] }}</span>
                            <span class="month">{{ getMonthName(event.date.split('-')[1]) }}</span>
                         </div>
                         <div class="event-body">
                            <p class="event-title">{{ event.title }}</p>
                            <p class="event-amount" v-if="event.amount">{{ event.amount }}</p>
                         </div>
                      </div>
                      <el-empty v-if="!calendarEvents.length" description="Подій немає" :image-size="60" />
                   </div>
                </div>

                <div class="official-tax-widget">
                   <div class="flex justify-between items-center mb-4">
                      <h4 class="m-0">📊 Дані ДПС</h4>
                      <el-button type="primary" :loading="taxUpdateLoading" @click="fetchOfficialRates">
                         🔄 Оновити з реєстрів
                      </el-button>
                   </div>
                   <div class="tax-info-card">
                      <div class="p-4 bg-blue-50 rounded mb-4" v-if="taxSettings.last_updated">
                          <span class="text-xs text-blue-600">Останнє успішне оновлення: <strong>{{ taxSettings.last_updated }}</strong></span>
                      </div>
                      <div class="tax-item mb-2 flex justify-between">
                         <span class="text-gray-500">ЄСВ (офіційно):</span>
                         <strong>{{ form.tax_amount_esv || '—' }} грн</strong>
                      </div>
                      <div class="tax-item mb-2 flex justify-between">
                         <span class="text-gray-500">Єдиний податок:</span>
                         <strong>{{ form.tax_rate_single || '—' }}</strong>
                      </div>
                      <div class="tax-item mb-2 flex justify-between">
                         <span class="text-gray-500">Військовий збір:</span>
                         <strong>{{ form.military_tax_rate || '—' }}</strong>
                      </div>
                   </div>
                </div>
             </el-col>
           </el-row>
        </el-tab-pane>

        <!-- BANK ACCOUNTS TAB -->
        <el-tab-pane label="Банківські рахунки" name="banks" lazy>
          <div class="tab-actions mb-4">
             <el-button type="primary" @click="openBankModal">
                <el-icon class="mr-2"><Plus /></el-icon> Додати рахунок
             </el-button>
          </div>

          <el-table :data="form.bank_accounts" border stripe style="width: 100%">
             <el-table-column prop="bank_name" label="Банк" width="180" />
             <el-table-column prop="iban" label="IBAN" min-width="260" />
             <el-table-column prop="currency" label="Валюта" width="100" />
             <el-table-column label="Статус" width="120">
                <template #default="scope">
                   <el-tag v-if="scope.row.is_primary" type="success">Основний</el-tag>
                </template>
             </el-table-column>
             <el-table-column label="Дії" width="150" fixed="right">
                <template #default="scope">
                   <el-button size="small" @click="editBank(scope.row)">Редаг.</el-button>
                   <el-button size="small" type="danger" link @click="deleteBank(scope.$index)">Видал.</el-button>
                </template>
             </el-table-column>
          </el-table>
        </el-tab-pane>

      </el-tabs>
    </el-card>

    <div v-else class="empty-selection">
       <el-empty description="Оберіть організацію для налаштування або додайте нову" />
    </div>

    <!-- BANK ACCOUNT MODAL -->
    <el-dialog v-model="bankModalVisible" title="Банківський рахунок" width="500px">
      <el-form label-position="top">
        <el-form-item label="IBAN Рахунок">
           <el-input v-model="bankForm.iban" placeholder="UA..." @input="handleIbanInput" />
           <div class="form-tip" v-if="bankForm.bank_name">Банк визначено: <strong>{{ bankForm.bank_name }}</strong></div>
        </el-form-item>
        <el-row :gutter="12">
           <el-col :span="12">
              <el-form-item label="Валюта">
                 <el-select v-model="bankForm.currency">
                    <el-option label="UAH (Гривня)" value="UAH" />
                    <el-option label="USD (Долар)" value="USD" />
                    <el-option label="EUR (Євро)" value="EUR" />
                 </el-select>
              </el-form-item>
           </el-col>
           <el-col :span="12">
               <el-form-item label="МФО" >
                  <el-input v-model="bankForm.mfo" readonly disabled placeholder="Автоматично" />
               </el-form-item>
           </el-col>
        </el-row>
        <el-form-item label="Назва в системі">
           <el-input v-model="bankForm.description" placeholder="Напр. Основний поточний" />
        </el-form-item>
        <el-form-item>
           <el-checkbox v-model="bankForm.is_primary">Зробити основним рахунком</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="bankModalVisible = false">Скасувати</el-button>
          <el-button type="primary" @click="saveBankAccount">Зберегти</el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Check, MagicStick, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { 
  getCompanies, 
  updateCompanySettings, 
  fetchEdrpouData, 
  createCompany, 
  setDefaultCompany,
  fetchOfficialTaxRates 
} from '@/api/company'

// State
const loading = ref(false)
const saving = ref(false)
const autofillLoading = ref(false)
const taxUpdateLoading = ref(false)
const activeTab = ref('general')
const bankModalVisible = ref(false)
const sameAddress = ref(true)

const companies = ref([])
const selectedCompany = ref(null)

const form = reactive({
  id: null,
  company_type: 'FOP',
  name: '',
  full_name_uk: '',
  full_name_en: '',
  website: '',
  email: '',
  phone: '',
  edrpou: '',
  ipn: '',
  kved: '',
  director_name: '',
  director_position: '',
  legal_address: '',
  physical_address: '',
  tax_group: '',
  vat_payer: false,
  tax_rate_single: '',
  tax_amount_esv: '',
  military_tax_rate: '',
  last_tax_update: '',
  fop_income_limit: null,
  bank_accounts: []
})

const incomeData = ref(null)
const calendarEvents = ref([])
const currentYear = ref(new Date().getFullYear())

// Advanced Tax Settings (stored in tax_settings JSON field)
const taxSettings = reactive({
  tax_year: 2026,
  min_wage: 8647,
  subsistence_min: 3328,
  esv_rate: 0.22,
  single_tax_rate: 0.20,
  military_levy_rate: 0.10, // Fixed for G1, G2
  military_levy_rate_percent: 0.01, // For G3
  limit_multiplier_g1: 167,
  limit_multiplier_g2: 834,
  limit_multiplier_g3: 1167,
  last_updated: null
})

// Computed calculations
const monthlyESV = computed(() => Math.round(taxSettings.min_wage * taxSettings.esv_rate * 100) / 100)
const monthlySingleTax = computed(() => {
  if (form.tax_group === 'GROUP_1') return Math.round(taxSettings.subsistence_min * 0.10 * 100) / 100
  if (form.tax_group === 'GROUP_2') return Math.round(taxSettings.min_wage * taxSettings.single_tax_rate * 100) / 100
  return 0 // For G3 it's based on income
})
const monthlyMilitary = computed(() => {
  if (['GROUP_1', 'GROUP_2'].includes(form.tax_group)) {
    return Math.round(taxSettings.min_wage * taxSettings.military_levy_rate * 100) / 100
  }
  return 0 // For G3 it's 1% of income
})
const monthlyTotal = computed(() => monthlyESV.value + monthlySingleTax.value + monthlyMilitary.value)

const incomeLimit = computed(() => {
  if (form.tax_group === 'GROUP_1') return taxSettings.min_wage * taxSettings.limit_multiplier_g1
  if (form.tax_group === 'GROUP_2') return taxSettings.min_wage * taxSettings.limit_multiplier_g2
  if (form.tax_group === 'GROUP_3') return taxSettings.min_wage * taxSettings.limit_multiplier_g3
  return 0
})

const bankForm = reactive({
  iban: '',
  bank_name: '',
  mfo: '',
  currency: 'UAH',
  description: '',
  is_primary: false
})

// Lifecycle
onMounted(async () => {
    fetchInitialData()
})

const fetchInitialData = async () => {
  loading.value = true
  try {
    const data = await getCompanies()
    companies.value = data
    if (data.length > 0) {
        selectCompany(data.find(c => c.is_default) || data[0])
    }
  } catch (e) {
    ElMessage.error('Не вдалося завантажити дані компаній')
  } finally {
    loading.value = false
  }
}

const selectCompany = (company) => {
    selectedCompany.value = company
    Object.keys(form).forEach(key => {
        if (Object.prototype.hasOwnProperty.call(company, key)) {
            form[key] = company[key]
        }
    })
    sameAddress.value = form.legal_address === form.physical_address
    
    // Reset tax settings or use from company JSON field
    if (company.tax_settings) {
      Object.assign(taxSettings, company.tax_settings)
    } else {
      // Fallback defaults
      Object.assign(taxSettings, {
        tax_year: 2026,
        min_wage: 8647,
        subsistence_min: 3328,
        last_updated: null
      })
    }
    
    // Fetch finance data
    fetchFinanceData(company.id)
}

const fetchFinanceData = async (companyId) => {
    try {
        const incomeRes = await api.get(`/api/v1/finance/fop-income?company_id=${companyId}`)
        incomeData.value = incomeRes.data
        const calendarRes = await api.get(`/api/v1/finance/fop-calendar?company_id=${companyId}`)
        calendarEvents.value = calendarRes.data
        
        // Also fetch tax settings from JSON endpoint
        const taxRes = await api.get('/api/v1/organization/tax-settings')
        if (taxRes.data && taxRes.data.tax_settings) {
          Object.assign(taxSettings, taxRes.data.tax_settings)
        }
    } catch (e) {
        console.error('Failed to fetch finance data', e)
    }
}

// Methods
const saveSettings = async () => {
  saving.value = true
  try {
    // 1. Update company general data
    const updated = await updateCompanySettings(form)
    
    // 2. Update tax settings JSON
    await api.put('/api/v1/organization/tax-settings', {
      settings: {
        ...taxSettings,
        tax_group: form.tax_group,
        vat_payer: form.vat_payer,
        fop_income_limit: incomeLimit.value
      }
    })
    
    // Update local list
    const idx = companies.value.findIndex(c => c.id === updated.id)
    if (idx !== -1) companies.value[idx] = updated
    
    ElMessage.success('Налаштування та податкові ставки збережено')
  } catch (e) {
    ElMessage.error('Помилка при збереженні')
  } finally {
    saving.value = false
  }
}

const createNewCompany = async () => {
    const fresh = { name: 'Нова організація', company_type: 'FOP', bank_accounts: [] }
    try {
        const created = await createCompany(fresh)
        companies.value.push(created)
        selectCompany(created)
        ElMessage.success('Нову організацію створено')
    } catch (e) {
        ElMessage.error('Помилка створення')
    }
}

const makeDefault = async (id) => {
    try {
        await setDefaultCompany(id)
        companies.value.forEach(c => c.is_default = (c.id === id))
        ElMessage.success('Фірму встановлено за замовчуванням')
    } catch (e) {
        ElMessage.error('Помилка')
    }
}

const fetchOfficialRates = async () => {
    if (!form.id) return
    taxUpdateLoading.value = true
    try {
        // Use the new AI-powered refresh endpoint
        const { data } = await api.post('/api/v1/organization/tax-settings/refresh')
        if (data.status === 'success') {
          const rates = data.data
          taxSettings.min_wage = rates.min_wage
          taxSettings.subsistence_min = rates.subsistence_min
          taxSettings.tax_year = rates.year
          taxSettings.last_updated = rates.last_updated
          
          Object.assign(form, {
            tax_amount_esv: rates.monthly.esv,
            tax_rate_single: rates.monthly.single_tax,
            last_tax_update: rates.last_updated
          })
          
          ElMessage.success('Дані успішно оновлено з реєстрів (AI)!')
        }
    } catch (e) {
        console.error('Error refreshing tax settings:', e)
        ElMessage.error('Помилка при оновленні даних')
    } finally {
        taxUpdateLoading.value = false
    }
}

const handleTypeChange = (val) => {
    form.director_position = val === 'FOP' ? 'ФОП' : 'Директор'
}

const handleSameAddress = (val) => {
    if (val) form.physical_address = form.legal_address
}

const autofillByEdrpou = async () => {
    if (!form.edrpou || form.edrpou.length < 8) {
        ElMessage.warning('Введіть коректний код ЄДРПОУ/РНОКПП')
        return
    }
    
    autofillLoading.value = true
    try {
        const data = await fetchEdrpouData(form.edrpou)
        if (data) {
            form.full_name_uk = data.full_name
            form.name = data.name
            form.legal_address = data.address
            if (sameAddress.value) form.physical_address = data.address
            form.director_name = data.director
            form.kved = data.kved
            ElMessage.success('Дані заповнено!')
        }
    } catch (e) {
        ElMessage.error('Помилка пошуку')
    } finally {
        autofillLoading.value = false
    }
}

// Bank Account Logic
const openBankModal = () => {
    Object.assign(bankForm, { iban: '', bank_name: '', mfo: '', currency: 'UAH', description: '', is_primary: false })
    bankModalVisible.value = true
}

const editBank = (row) => {
     Object.assign(bankForm, row)
     bankModalVisible.value = true
}

const deleteBank = (index) => {
    form.bank_accounts.splice(index, 1)
}

const handleIbanInput = (val) => {
    if (val.length >= 10 && val.toUpperCase().startsWith('UA')) {
        const mfo = val.substring(4, 10)
        bankForm.mfo = mfo
        const banks = { '305299': 'ПриватБанк', '322001': 'Monobank', '300023': 'KredoBank' }
        bankForm.bank_name = banks[mfo] || 'Інший Банк'
    }
}

const saveBankAccount = () => {
    if (!bankForm.iban) return
    if (bankForm.is_primary) form.bank_accounts.forEach(b => b.is_primary = false)
    
    const existingIdx = form.bank_accounts.findIndex(b => b.iban === bankForm.iban)
    if (existingIdx !== -1) form.bank_accounts[existingIdx] = { ...bankForm }
    else form.bank_accounts.push({ ...bankForm, id: Date.now() })
    
    bankModalVisible.value = false
}

// Finance Helpers
const formatCurrency = (v) => Number(v || 0).toLocaleString('uk-UA')

const getProgressStatus = (pct) => {
    if (pct >= 95) return 'exception'
    if (pct >= 85) return 'warning'
    return 'success'
}

const getMonthName = (m) => {
    const months = ['січ', 'лют', 'бер', 'кві', 'тра', 'чер', 'лип', 'сер', 'вер', 'жов', 'лис', 'гру']
    return months[parseInt(m) - 1] || m
}
</script>

<style scoped>
.company-settings-page {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.subtitle {
    color: #909399;
    margin: 4px 0 0;
}

.companies-grid {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}

.company-card {
    width: 100%;
    margin-bottom: 12px;
    cursor: pointer;
    transition: all 0.3s;
    border: 2px solid transparent;
    position: relative;
}

.company-card:hover {
    transform: translateY(-4px);
}

.company-card.active {
    border-color: #409eff;
    background-color: #f0f7ff;
}

.card-status {
    position: absolute;
    top: 10px;
    right: 10px;
}

.company-card h3 {
    margin: 0 0 8px 0;
    font-size: 16px;
}

.type-tag {
    font-size: 12px;
    color: #909399;
    margin-bottom: 4px;
}

.edrpou {
    font-size: 13px;
    font-weight: 600;
}

.official-tax-widget {
    background: #fff;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.tax-info-card {
    margin-top: 16px;
}

.tax-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    font-size: 14px;
}

.form-section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
  border-bottom: 2px solid #f0f2f5;
  padding-bottom: 8px;
}

.monthly-payments-card {
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}

.payment-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.payment-item.total {
  font-weight: 700;
  font-size: 1.1rem;
  color: #409eff;
}

.payment-item .label {
  color: #606266;
}

.payment-item .value {
  color: #303133;
}

.tax-limit-info {
  background: #f8fafc;
  border-left: 4px solid #409eff;
}

.settings-card {
    min-height: 500px;
}

.form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
}

.tab-actions {
    display: flex;
    justify-content: flex-end;
}

/* FOP Income Widget Styles */
.income-widget {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.widget-header h4 {
    margin: 0;
    font-size: 16px;
    color: #475569;
}

.total-amount {
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
}

.progress-section {
    margin-bottom: 24px;
}

.progress-labels {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: #64748b;
    margin-bottom: 8px;
}

.progress-footer {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #94a3b8;
    margin-top: 8px;
}

.quarters-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    border-top: 1px solid #f1f5f9;
    padding-top: 16px;
}

.q-item {
    text-align: center;
}

.q-item .q-name {
    display: block;
    font-size: 11px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 4px;
}

.q-item .q-val {
    font-size: 14px;
    font-weight: 600;
    color: #334155;
}

.accounts-breakdown .section-sub {
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    margin-bottom: 12px;
}

.acc-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #f8fafc;
}

.acc-info {
    display: flex;
    flex-direction: column;
}

.acc-name {
    font-size: 13px;
    font-weight: 500;
    color: #1e293b;
}

.acc-iban {
    font-size: 11px;
    color: #94a3b8;
}

.acc-val {
    font-size: 13px;
    font-weight: 600;
    color: #0f172a;
}

/* Tax Calendar Styles */
.tax-calendar-widget {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
}

.tax-calendar-widget h4 {
    margin: 0 0 16px 0;
    font-size: 15px;
    color: #475569;
}

.calendar-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.calendar-item {
    display: flex;
    gap: 16px;
    align-items: center;
    padding: 12px;
    background: #f8fafc;
    border-radius: 8px;
    border-left: 4px solid #6366f1;
}

.event-date {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 45px;
}

.event-date .day {
    font-size: 18px;
    font-weight: 700;
    color: #1e293b;
    line-height: 1;
}

.event-date .month {
    font-size: 11px;
    text-transform: uppercase;
    color: #64748b;
    margin-top: 2px;
}

.event-body .event-title {
    margin: 0;
    font-size: 13px;
    font-weight: 600;
    color: #334155;
}

.event-body .event-amount {
    margin: 2px 0 0 0;
    font-size: 12px;
    color: #6366f1;
    font-weight: 500;
}

.mt-6 { margin-top: 24px; }
.mb-6 { margin-bottom: 24px; }
</style>
