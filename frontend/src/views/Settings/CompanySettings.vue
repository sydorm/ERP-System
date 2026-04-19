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
                  <el-form-item label="Система оподаткування">
                      <el-select v-model="form.tax_group" placeholder="Оберіть групу">
                        <el-option label="1 група (ФОП)" value="GROUP_1" />
                        <el-option label="2 група (ФОП)" value="GROUP_2" />
                        <el-option label="3 група (ФОП/ТОВ) - 5%" value="GROUP_3" />
                        <el-option label="Загальна система" value="GENERAL" />
                      </el-select>
                  </el-form-item>

                  <el-row :gutter="12">
                    <el-col :span="12">
                      <el-form-item label="Ліміт доходу на рік (грн)">
                        <el-input-number v-model="form.fop_income_limit" :min="0" style="width: 100%" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                       <el-form-item label="Військовий збір (%)">
                         <el-input v-model="form.military_tax_rate" />
                       </el-form-item>
                    </el-col>
                  </el-row>

                  <el-form-item>
                    <el-checkbox v-model="form.vat_payer" border>Платник ПДВ</el-checkbox>
                  </el-form-item>

                  <el-form-item label="Індивідуальний податковий номер (ІПН)" v-if="form.vat_payer">
                      <el-input v-model="form.ipn" placeholder="12 цифр" />
                  </el-form-item>
                </el-form>

                <!-- FOP INCOME WIDGET -->
                <div class="income-widget mt-6" v-if="incomeData">
                  <div class="widget-header">
                    <h4>💳 Дохід ФОП за {{ currentYear }} рік</h4>
                    <span class="total-amount">{{ formatCurrency(incomeData.total) }} грн</span>
                  </div>
                  
                  <div class="progress-section">
                    <div class="progress-labels">
                      <span>Прогрес до ліміту</span>
                      <span>{{ incomeData.percentage.toFixed(1) }}%</span>
                    </div>
                    <el-progress 
                      :percentage="Math.min(incomeData.percentage, 100)" 
                      :status="getProgressStatus(incomeData.percentage)"
                      :stroke-width="12"
                      :show-text="false"
                    />
                    <div class="progress-footer">
                      <span>Залишок: <strong>{{ formatCurrency(incomeData.remaining) }} грн</strong></span>
                      <span>Ліміт: {{ formatCurrency(incomeData.limit) }} грн</span>
                    </div>
                  </div>

                  <div class="quarters-grid mt-4">
                    <div v-for="(q, idx) in incomeData.quarters" :key="idx" class="q-item">
                      <span class="q-name">Q{{ idx + 1 }}</span>
                      <span class="q-val">{{ formatCurrency(q) }}</span>
                    </div>
                  </div>

                  <div class="accounts-breakdown mt-4">
                    <p class="section-sub">По рахунках:</p>
                    <div v-for="acc in incomeData.by_account" :key="acc.iban" class="acc-row">
                      <div class="acc-info">
                        <span class="acc-name">{{ acc.account_name }}</span>
                        <span class="acc-iban">{{ acc.iban }}</span>
                      </div>
                      <span class="acc-val">{{ formatCurrency(acc.amount) }} грн</span>
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
                   <h4>📊 Ставки та платежі</h4>
                   <div class="tax-info-card">
                      <div class="tax-item">
                         <span>ЄСВ (щомісячно):</span>
                         <strong>{{ form.tax_amount_esv || '—' }} грн</strong>
                      </div>
                      <div class="tax-item">
                         <span>Єдиний податок:</span>
                         <strong>{{ form.tax_rate_single || '—' }}</strong>
                      </div>
                      <el-divider />
                      <div class="update-info">
                         <span v-if="form.last_tax_update">Оновлено: {{ form.last_tax_update }}</span>
                         <el-button type="primary" link @click="fetchOfficialRates" :loading="taxUpdateLoading">
                            Оновити з реєстрів
                         </el-button>
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
import { ref, reactive, onMounted } from 'vue'
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
const currentYear = new Date().getFullYear()

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
    // Avoid deep cloning the whole object if we can just copy properties
    // This reduces the reactivity noise
    Object.keys(form).forEach(key => {
        if (Object.prototype.hasOwnProperty.call(company, key)) {
            form[key] = company[key]
        }
    })
    sameAddress.value = form.legal_address === form.physical_address
    
    // Fetch finance data
    fetchFinanceData(company.id)
}

const fetchFinanceData = async (companyId) => {
    try {
        const [incomeRes, calendarRes] = await Promise.all([
            api.get(`/api/v1/finance/fop-income?company_id=${companyId}`),
            api.get(`/api/v1/finance/fop-calendar?company_id=${companyId}`)
        ])
        incomeData.value = incomeRes.data
        calendarEvents.value = calendarRes.data
    } catch (e) {
        console.error('Failed to fetch finance data', e)
    }
}

// Methods
const saveSettings = async () => {
  saving.value = true
  try {
    const updated = await updateCompanySettings(form)
    // Update local list
    const idx = companies.value.findIndex(c => c.id === updated.id)
    if (idx !== -1) companies.value[idx] = updated
    
    ElMessage.success('Налаштування збережено')
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
        const rates = await fetchOfficialTaxRates(form.id)
        Object.assign(form, rates)
        ElMessage.success('Офіційні ставки оновлено')
    } catch (e) {
        ElMessage.error('Помилка оновлення даних ДПС')
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
  max-width: 1200px;
  margin: 0 auto;
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
    width: 280px;
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
    background: #f8fafc;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
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

.update-info {
    font-size: 12px;
    color: #94a3b8;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
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
