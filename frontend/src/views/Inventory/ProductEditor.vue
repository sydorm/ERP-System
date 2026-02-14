<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
         <el-button :icon="ArrowLeft" circle @click="goBack" />
         <h2>{{ isEditMode ? 'Редагування товару' : 'Новий товар' }}</h2>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">Скасувати</el-button>
        <el-button type="primary" :loading="submitting" @click="saveProduct">
            Зберегти
        </el-button>
      </div>
    </div>

    <div class="editor-content">
      <el-tabs v-model="activeTab" class="product-tabs">
        <!-- 1. General Info -->
        <el-tab-pane label="Загальна інформація" name="general">
          <el-card shadow="never" class="tab-card">
            <el-form ref="generalFormRef" :model="form" :rules="formRules" label-position="top">
              <el-row :gutter="40">
                <el-col :span="16">
                  <el-form-item label="Назва товару" prop="name">
                    <el-input v-model="form.name" size="large" placeholder="Введіть назву (напр., Нога стола чорна 710мм)" />
                  </el-form-item>
                  
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="Артикул (SKU)" prop="sku">
                        <el-input v-model="form.sku" placeholder="WOOD-001" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="Категорія" prop="category">
                         <el-select v-model="form.category" placeholder="Оберіть категорію" style="width: 100%">
                            <el-option v-for="opt in categoryOptions" :key="opt.code" :label="opt.name" :value="opt.code" />
                         </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-form-item label="Опис товару">
                    <el-input v-model="form.description" type="textarea" :rows="5" placeholder="Докладний опис товару, технічні характеристики..." />
                  </el-form-item>
                </el-col>

                <el-col :span="8">
                   <el-form-item label="Зображення">
                      <div class="image-upload-zone">
                         <el-image v-if="form.image_url" :src="form.image_url" fit="cover" class="preview-image" />
                         <div v-else class="upload-placeholder">
                            <el-icon :size="40"><Picture /></el-icon>
                            <span>Натисніть для завантаження</span>
                         </div>
                      </div>
                   </el-form-item>
                   
                   <el-form-item label="Одиниця виміру">
                      <el-select v-model="form.unit_of_measure" style="width: 100%">
                         <el-option v-for="opt in uomOptions" :key="opt.code" :label="opt.name" :value="opt.code" />
                      </el-select>
                   </el-form-item>

                   <el-form-item label="Статус">
                      <el-switch v-model="form.is_active" active-text="Активний" inactive-text="Архівний" />
                   </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>
        </el-tab-pane>

        <!-- 2. Commercial -->
        <el-tab-pane label="Ціни та Комерція" name="pricing">
          <el-card shadow="never" class="tab-card">
            <el-row :gutter="40">
               <el-col :span="12">
                  <h3>Ціноутворення</h3>
                  <el-form label-position="left" label-width="150px" style="margin-top: 20px">
                    <el-form-item label="Ціна продажу">
                      <el-input-number v-model="form.price" :precision="2" :step="1" style="width: 200px" />
                      <el-select v-model="form.currency" style="width: 100px; margin-left: 10px">
                        <el-option v-for="c in currencyOptions" :key="c.code" :label="c.code" :value="c.code" />
                      </el-select>
                    </el-form-item>
                    
                    <el-form-item label="Собівартість">
                       <el-input-number v-model="form.cost" :precision="2" :step="1" style="width: 200px" />
                       <span class="cost-hint" v-if="hasSpecification">Рахується автоматично за специфікацією</span>
                    </el-form-item>

                    <el-form-item label="Націнка (%)">
                       <el-tag type="success" size="large" effect="dark">
                          {{ calculateMarkup }}%
                       </el-tag>
                    </el-form-item>
                  </el-form>
               </el-col>
               
               <el-col :span="12">
                  <div class="chart-placeholder">
                    <el-empty description="Тут буде графік історії зміни цін" />
                  </div>
               </el-col>
            </el-row>
          </el-card>
        </el-tab-pane>

        <!-- 3. Specification (BOM) -->
        <el-tab-pane label="Специфікація (BOM)" name="specification">
          <el-card shadow="never" class="tab-card">
             <div class="tab-header-tiny">
                <h3>Склад виробу</h3>
                <el-button type="primary" size="small" :icon="Plus">Додати матеріал</el-button>
             </div>
             
             <el-table :data="specificationItems" stripe style="width: 100%; margin-top: 15px">
                <el-table-column prop="sku" label="Артикул" width="120" />
                <el-table-column prop="name" label="Назва компонента" />
                <el-table-column prop="quantity" label="Кількість" width="120">
                   <template #default="scope">
                      <el-input-number v-model="scope.row.quantity" size="small" :min="0.0001" style="width: 100px" />
                   </template>
                </el-table-column>
                <el-table-column prop="uom" label="Од." width="80" />
                <el-table-column prop="cost" label="Вартість" width="120" align="right">
                    <template #default="scope">
                       {{ formatCurrency(scope.row.quantity * scope.row.unitPrice, 'UAH') }}
                    </template>
                </el-table-column>
                <el-table-column label="Дії" width="80" align="right">
                   <template #default="scope">
                      <el-button link type="danger" :icon="Delete" />
                   </template>
                </el-table-column>
             </el-table>

             <div class="bom-footer">
                <div class="bom-total">
                   Загальна собівартість матеріалів: <strong>{{ formatCurrency(totalBomCost, 'UAH') }}</strong>
                </div>
             </div>
          </el-card>
        </el-tab-pane>

        <!-- 4. Warehouse -->
        <el-tab-pane label="Складські запаси" name="inventory">
          <el-card shadow="never" class="tab-card">
             <h3>Поточні залишки</h3>
             <el-table :data="stockLevels" border style="width: 100%; margin-top: 15px">
                <el-table-column prop="warehouse" label="Склад" />
                <el-table-column prop="quantity" label="Наявність" width="150" align="center" />
                <el-table-column prop="reserved" label="Резерв" width="150" align="center" />
                <el-table-column prop="available" label="Доступно" width="150" align="center" />
                <el-table-column prop="minLevel" label="Мін. очікування" width="150" align="center">
                   <template #default="scope">
                      <el-input-number v-model="scope.row.minLevel" size="small" />
                   </template>
                </el-table-column>
             </el-table>
          </el-card>
        </el-tab-pane>

        <!-- 5. Files -->
        <el-tab-pane label="Файли та техдокументація" name="files">
           <el-card shadow="never" class="tab-card">
              <el-upload
                class="upload-demo"
                drag
                action="#"
                multiple
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  Перетягніть файли сюди або <em>натисніть для завантаження</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    Креслення, сертифікати, PDF-інструкції (до 10MB)
                  </div>
                </template>
              </el-upload>
           </el-card>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Picture, Plus, Delete, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const route = useRoute()
const router = useRouter()

// State
const activeTab = ref('general')
const submitting = ref(false)
const loading = ref(false)
const isEditMode = computed(() => !!route.params.id)

const form = reactive({
    id: null,
    sku: '',
    name: '',
    description: '',
    category: '',
    unit_of_measure: 'шт',
    price: 0,
    cost: 0,
    currency: 'UAH',
    image_url: '',
    is_active: true
})

// Options
const uomOptions = ref([])
const categoryOptions = ref([])
const currencyOptions = ref([])

// Mocked data for UI demonstration
const specificationItems = ref([])
const stockLevels = ref([])
const hasSpecification = ref(false)

const calculateMarkup = computed(() => {
    if (!form.price || !form.cost) return 0
    return (((form.price - form.cost) / form.cost) * 100).toFixed(1)
})

const totalBomCost = computed(() => {
    return specificationItems.value.reduce((acc, item) => acc + (item.quantity * item.unitPrice), 0)
})

const goBack = () => {
    router.push('/inventory/nomenclature')
}

const fetchDictionaries = async () => {
    try {
        const [uomRes, catRes, currRes] = await Promise.all([
            api.get('/api/v1/dictionaries/UOM'),
            api.get('/api/v1/dictionaries/PRODUCT_CATEGORY'),
            api.get('/api/v1/dictionaries/CURRENCY')
        ])
        uomOptions.value = uomRes.data
        categoryOptions.value = catRes.data
        currencyOptions.value = currRes.data
    } catch (error) {
        console.error('Failed to load dictionaries', error)
    }
}

const fetchProduct = async () => {
    if (!isEditMode.value) return
    loading.value = true
    try {
        const res = await api.get(`/api/v1/products/${route.params.id}`)
        Object.assign(form, res.data)
        // Load stock levels
        fetchStockLevels()
    } catch (e) {
        ElMessage.error('Помилка завантаження товару')
    } finally {
        loading.value = false
    }
}

const fetchStockLevels = async () => {
    try {
        const res = await api.get(`/api/v1/products/${route.params.id}/stock`)
        stockLevels.value = res.data
    } catch (e) {
        console.error('Failed to load stock levels', e)
    }
}

const saveProduct = async () => {
    submitting.value = true
    try {
        if (isEditMode.value) {
            await api.put(`/api/v1/products/${form.id}`, form)
            ElMessage.success('Товар оновлено')
        } else {
            const res = await api.post('/api/v1/products', form)
            ElMessage.success('Товар створено')
            router.push(`/inventory/nomenclature/${res.data.id}`)
        }
    } catch (error) {
        ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
    } finally {
        submitting.value = false
    }
}

const formatCurrency = (val, curr) => {
    return new Intl.NumberFormat('uk-UA', { style: 'currency', currency: curr || 'UAH' }).format(val)
}

onMounted(() => {
    fetchDictionaries()
    fetchProduct()
})
</script>

<style scoped>
.page-container {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    padding: 16px 24px;
    border-bottom: 1px solid #eef0f2;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 16px;
}

.header-left h2 {
    margin: 0;
    font-size: 20px;
}

.editor-content {
    flex: 1;
    overflow-y: auto;
    background: #f8f9fa;
}

.product-tabs {
    height: 100%;
}

:deep(.el-tabs__header) {
    background: white;
    padding: 0 24px;
    margin-bottom: 0;
}

.tab-card {
    margin: 24px;
    border: 1px solid #eef0f2;
}

.image-upload-zone {
    width: 100%;
    height: 200px;
    border: 2px dashed #dcdfe6;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    background: white;
    transition: all 0.2s;
}

.image-upload-zone:hover {
    border-color: #409eff;
    color: #409eff;
}

.upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    color: #909399;
}

.preview-image {
    width: 100%;
    height: 100%;
    border-radius: 6px;
}

.cost-hint {
    margin-left: 12px;
    font-size: 12px;
    color: #909399;
    font-style: italic;
}

.tab-header-tiny {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.bom-footer {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #eef0f2;
    text-align: right;
}

.bom-total {
    font-size: 16px;
}

.bom-total strong {
    color: #409eff;
}

.chart-placeholder {
    height: 300px;
    background: #fdfdfd;
    border: 1px dashed #ebeef5;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
