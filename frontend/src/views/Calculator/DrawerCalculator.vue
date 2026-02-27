<template>
  <div class="calc-root">
    <!-- Header -->
    <div class="calc-header">
      <div class="calc-header-inner">
        <div class="calc-logo">
          <span class="calc-logo-icon">🪵</span>
          <div>
            <h1>Конструктор шухляд</h1>
            <p>Швидкий розрахунок вартості виробу</p>
          </div>
        </div>
        <a href="/calculator/admin" class="btn-admin">⚙️ Налаштування цін</a>
      </div>
    </div>

    <div class="calc-body">
      <!-- Mode Tabs -->
      <div class="mode-tabs">
        <button :class="['mode-tab', { active: mode === 'manual' }]" @click="mode = 'manual'">
          📐 Ручний конструктор
        </button>
        <button :class="['mode-tab', { active: mode === 'ai' }]" @click="mode = 'ai'">
          🤖 AI-аналіз фото
        </button>
      </div>

      <!-- ═══ AI MODE ═══════════════════════════════════════════════════════ -->
      <div v-if="mode === 'ai'" class="ai-panel">
        <div class="ai-upload-area"
             :class="{ 'drag-over': isDragging }"
             @dragover.prevent="isDragging = true"
             @dragleave="isDragging = false"
             @drop.prevent="onDrop">
          <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFileChange" />
          <div v-if="!previewUrl" class="ai-upload-placeholder" @click="$refs.fileInput.click()">
            <div class="ai-upload-icon">📸</div>
            <p>Перетягніть фото шухляди або <span class="link">натисніть тут</span></p>
            <small>JPG, PNG, WEBP до 10МБ</small>
          </div>
          <div v-else class="ai-preview">
            <img :src="previewUrl" alt="preview" />
            <button class="btn-change-img" @click="$refs.fileInput.click()">Змінити фото</button>
          </div>
        </div>

        <button class="btn-analyze" :disabled="!selectedFile || aiLoading" @click="analyzeImage">
          <span v-if="aiLoading">🔄 Аналізую...</span>
          <span v-else>🤖 Аналізувати фото</span>
        </button>

        <div v-if="aiResult" class="ai-result-box">
          <div class="ai-result-header">
            <span>✅ AI визначив:</span>
            <span :class="['ai-confidence', aiResult.confidence]">
              {{ aiResult.confidence === 'high' ? '🟢 Впевнено' : '🟡 Орієнтовно' }}
            </span>
          </div>
          <p class="ai-notes">{{ aiResult.notes }}</p>
          <button class="btn-apply-ai" @click="applyAiResult">
            ↓ Заповнити конструктор цими даними
          </button>
        </div>
      </div>

      <!-- ═══ MANUAL CONSTRUCTOR ════════════════════════════════════════════ -->
      <div class="constructor">
        <!-- STEP 1: Тип фасаду -->
        <div class="step-card">
          <div class="step-label"><span class="step-num">1</span> Тип фасаду</div>
          <div class="type-grid">
            <div v-for="ft in facadeTypes" :key="ft.value"
                 :class="['type-card', { selected: form.facade_type === ft.value }]"
                 @click="form.facade_type = ft.value">
              <div class="type-icon">{{ ft.icon }}</div>
              <div class="type-name">{{ ft.label }}</div>
            </div>
          </div>
        </div>

        <!-- STEP 2: Напрямок -->
        <div class="step-card">
          <div class="step-label"><span class="step-num">2</span> Розташування шухляд</div>
          <div class="type-grid type-grid-2">
            <div :class="['type-card', { selected: form.direction === 'vertical' }]"
                 @click="form.direction = 'vertical'">
              <div class="type-icon dir-icon">
                <div class="dir-vertical"><div v-for="i in 3" :key="i" class="dir-row"></div></div>
              </div>
              <div class="type-name">В стовпець</div>
            </div>
            <div :class="['type-card', { selected: form.direction === 'horizontal' }]"
                 @click="form.direction = 'horizontal'">
              <div class="type-icon dir-icon">
                <div class="dir-horizontal"><div v-for="i in 3" :key="i" class="dir-col"></div></div>
              </div>
              <div class="type-name">В рядок</div>
            </div>
          </div>
        </div>

        <!-- STEP 3: Кількість + розміри -->
        <div class="step-card">
          <div class="step-label"><span class="step-num">3</span> Розміри та кількість</div>
          <div class="dims-grid">
            <div class="dim-field">
              <label>К-сть шухляд</label>
              <div class="count-control">
                <button @click="form.drawer_count = Math.max(1, form.drawer_count - 1)">−</button>
                <span>{{ form.drawer_count }}</span>
                <button @click="form.drawer_count = Math.min(8, form.drawer_count + 1)">+</button>
              </div>
            </div>
            <div class="dim-field">
              <label>Ширина короба (мм)</label>
              <input v-model.number="form.box_width" type="number" min="200" max="2400" />
            </div>
            <div class="dim-field">
              <label>Висота короба (мм)</label>
              <input v-model.number="form.box_height" type="number" min="100" max="2400" />
            </div>
            <div class="dim-field">
              <label>Глибина короба (мм)</label>
              <input v-model.number="form.box_depth" type="number" min="200" max="800" />
            </div>
            <div class="dim-field">
              <label>Глибина шухляди (мм)</label>
              <input v-model.number="form.drawer_depth" type="number" min="200" max="600" />
            </div>
          </div>

          <!-- Схема-прев'ю корпусу -->
          <div class="box-preview">
            <div class="box-preview-cabinet" :style="cabinetStyle">
              <div v-for="i in form.drawer_count" :key="i"
                   :class="['box-preview-drawer', { horizontal: form.direction === 'horizontal' }]">
                <div class="drawer-facade" v-if="form.facade_type !== 'none'">
                  {{ form.facade_type === 'overlay' ? '▪' : '◦' }}
                </div>
              </div>
            </div>
            <div class="box-preview-label">{{ form.box_width }} × {{ form.box_height }} мм</div>
          </div>
        </div>

        <!-- STEP 4: Матеріали та фурнітура -->
        <div class="step-card">
          <div class="step-label"><span class="step-num">4</span> Матеріали та фурнітура</div>
          <div class="select-grid">
            <div class="select-field">
              <label>Основний матеріал (ЛДСП)</label>
              <select v-model.number="form.main_material_id">
                <option v-for="m in materials" :key="m.id" :value="m.id">
                  {{ m.name }} — {{ m.price_per_m2 }} грн/м²
                </option>
              </select>
            </div>
            <div class="select-field">
              <label>Матеріал дна (ДВП)</label>
              <select v-model="form.bottom_material_id">
                <option :value="null">— як основний —</option>
                <option v-for="m in materials" :key="m.id" :value="m.id">
                  {{ m.name }} — {{ m.price_per_m2 }} грн/м²
                </option>
              </select>
            </div>
            <div class="select-field">
              <label>Напрямні</label>
              <select v-model="form.hardware_id">
                <option :value="null">— без напрямних —</option>
                <option v-for="h in hardware" :key="h.id" :value="h.id">
                  {{ h.name }} — {{ h.price_per_unit }} грн/{{ h.unit }}
                </option>
              </select>
            </div>
          </div>
          <!-- Послуги -->
          <div class="services-list">
            <div class="services-label">Послуги:</div>
            <div class="service-checkboxes">
              <label v-for="svc in services" :key="svc.id" class="service-check">
                <input type="checkbox" :value="svc.id" v-model="form.service_ids" />
                {{ svc.name }} — {{ svc.price }} грн/{{ svc.unit }}
              </label>
            </div>
          </div>
        </div>

        <!-- STEP 5: Клієнт -->
        <div class="step-card">
          <div class="step-label"><span class="step-num">5</span> Клієнт (необов'язково)</div>
          <div class="dims-grid">
            <div class="dim-field" style="grid-column: span 2">
              <label>Ім'я клієнта</label>
              <input v-model="form.client_name" type="text" placeholder="Іванов Іван" />
            </div>
            <div class="dim-field" style="grid-column: span 2">
              <label>Примітки</label>
              <input v-model="form.notes" type="text" placeholder="Колір, особливості..." />
            </div>
          </div>
        </div>

        <!-- Calculate button -->
        <button class="btn-calculate" :disabled="calculating || !form.main_material_id" @click="calculate">
          <span v-if="calculating">🔄 Рахую...</span>
          <span v-else>📊 Розрахувати вартість</span>
        </button>
      </div>

      <!-- ═══ RESULTS ══════════════════════════════════════════════════════ -->
      <div v-if="result" class="results-panel" id="results">
        <div class="results-header">
          <h2>📋 Розкрій та вартість</h2>
          <div class="results-actions">
            <button class="btn-save" @click="saveQuote">💾 Зберегти</button>
            <button class="btn-print" @click="printResult">🖨️ Друк</button>
          </div>
        </div>

        <div class="result-summary-box">
          <div class="summary-text">{{ result.summary }}</div>
        </div>

        <table class="details-table">
          <thead>
            <tr>
              <th>Деталь</th>
              <th>Матеріал</th>
              <th>Ш × В (мм)</th>
              <th>К-сть</th>
              <th>Площа м²</th>
              <th>Вартість</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in result.details" :key="d.name">
              <td>{{ d.name }}</td>
              <td class="mat-cell">{{ d.material }}</td>
              <td class="dim-cell">{{ d.width_mm }} × {{ d.height_mm }}</td>
              <td class="qty-cell">{{ d.quantity }} шт</td>
              <td>{{ d.area_m2 }} м²</td>
              <td class="price-cell">{{ d.price.toFixed(0) }} грн</td>
            </tr>
          </tbody>
        </table>

        <div class="totals-grid">
          <div class="total-row">
            <span>Матеріали:</span>
            <strong>{{ result.materials_total.toFixed(0) }} грн</strong>
          </div>
          <div class="total-row" v-if="result.hardware_total > 0">
            <span>Фурнітура:</span>
            <strong>{{ result.hardware_total.toFixed(0) }} грн</strong>
          </div>
          <div class="total-row" v-if="result.services_total > 0">
            <span>Послуги:</span>
            <strong>{{ result.services_total.toFixed(0) }} грн</strong>
          </div>
          <div class="total-row grand">
            <span>РАЗОМ:</span>
            <strong>{{ result.grand_total.toFixed(0) }} грн</strong>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast notification -->
    <div v-if="toast.show" :class="['toast', toast.type]">{{ toast.msg }}</div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ── State ──────────────────────────────────────────────────────────────────
const mode = ref('manual')
const materials = ref([])
const hardware = ref([])
const services = ref([])
const result = ref(null)
const calculating = ref(false)
const aiLoading = ref(false)
const aiResult = ref(null)
const selectedFile = ref(null)
const previewUrl = ref(null)
const isDragging = ref(false)
const toast = reactive({ show: false, msg: '', type: 'success' })
const fileInput = ref(null)

const facadeTypes = [
  { value: 'overlay', icon: '🟫', label: 'Накладний' },
  { value: 'inset', icon: '⬛', label: 'Врізний' },
  { value: 'none', icon: '⬜', label: 'Без фасаду' }
]

const form = reactive({
  drawer_count: 2,
  direction: 'vertical',
  facade_type: 'overlay',
  box_width: 600,
  box_height: 720,
  box_depth: 560,
  drawer_depth: 450,
  main_material_id: null,
  bottom_material_id: null,
  facade_material_id: null,
  hardware_id: null,
  service_ids: [],
  client_name: '',
  notes: ''
})

// ── Computed ────────────────────────────────────────────────────────────────
const cabinetStyle = computed(() => ({
  width: '120px',
  height: `${Math.max(80, Math.min(200, form.box_height / 4))}px`,
  display: form.direction === 'horizontal' ? 'flex' : 'block'
}))

// ── Lifecycle ───────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([loadMaterials(), loadHardware(), loadServices()])
})

async function loadMaterials() {
  const r = await fetch(`${API}/api/calculator/materials`)
  materials.value = await r.json()
  if (materials.value.length) form.main_material_id = materials.value[0].id
  const dvp = materials.value.find(m => m.name.includes('ДВП'))
  if (dvp) form.bottom_material_id = dvp.id
}
async function loadHardware() {
  const r = await fetch(`${API}/api/calculator/hardware`)
  hardware.value = await r.json()
}
async function loadServices() {
  const r = await fetch(`${API}/api/calculator/services`)
  services.value = await r.json()
}

// ── Calculate ───────────────────────────────────────────────────────────────
async function calculate() {
  calculating.value = true
  result.value = null
  try {
    const payload = { ...form }
    const r = await fetch(`${API}/api/calculator/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!r.ok) { const e = await r.json(); throw new Error(e.detail) }
    result.value = await r.json()
    setTimeout(() => document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' }), 100)
  } catch (e) {
    showToast('Помилка: ' + e.message, 'error')
  } finally {
    calculating.value = false
  }
}

// ── AI Image ────────────────────────────────────────────────────────────────
function onFileChange(e) {
  const f = e.target.files[0]
  if (f) setFile(f)
}
function onDrop(e) {
  isDragging.value = false
  const f = e.dataTransfer.files[0]
  if (f && f.type.startsWith('image/')) setFile(f)
}
function setFile(f) {
  selectedFile.value = f
  previewUrl.value = URL.createObjectURL(f)
  aiResult.value = null
}

async function analyzeImage() {
  if (!selectedFile.value) return
  aiLoading.value = true
  try {
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    const r = await fetch(`${API}/api/calculator/analyze-image`, { method: 'POST', body: fd })
    if (!r.ok) throw new Error('Помилка аналізу')
    aiResult.value = await r.json()
  } catch (e) {
    showToast('AI помилка: ' + e.message, 'error')
  } finally {
    aiLoading.value = false
  }
}

function applyAiResult() {
  if (!aiResult.value) return
  const a = aiResult.value
  form.drawer_count = a.drawer_count || form.drawer_count
  form.direction = a.direction || form.direction
  form.facade_type = a.facade_type || form.facade_type
  form.box_width = a.approx_width || form.box_width
  form.box_height = a.approx_height || form.box_height
  form.box_depth = a.approx_depth || form.box_depth
  form.drawer_depth = a.drawer_depth || form.drawer_depth
  mode.value = 'manual'
  showToast('Дані застосовано! Перевірте і натисніть Розрахувати.', 'success')
}

// ── Save ────────────────────────────────────────────────────────────────────
async function saveQuote() {
  if (!result.value) return
  try {
    await fetch(`${API}/api/calculator/save-quote?` + new URLSearchParams(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ inp: form, result: result.value })
    })
    showToast('Розрахунок збережено!', 'success')
  } catch {
    showToast('Не вдалось зберегти', 'error')
  }
}

function printResult() {
  window.print()
}

function showToast(msg, type = 'success') {
  toast.msg = msg; toast.type = type; toast.show = true
  setTimeout(() => (toast.show = false), 3500)
}
</script>

<style scoped>
/* ── Root ─── */
.calc-root {
  min-height: 100vh;
  background: #f1f3f8;
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ── Header ─── */
.calc-header {
  background: linear-gradient(135deg, #1a2332 0%, #2d3f5e 100%);
  padding: 0 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.25);
}
.calc-header-inner {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 0;
}
.calc-logo { display: flex; align-items: center; gap: 14px; }
.calc-logo-icon { font-size: 40px; }
.calc-logo h1 { margin: 0; font-size: 22px; color: #fff; font-weight: 700; }
.calc-logo p { margin: 2px 0 0; font-size: 13px; color: #9eb5d8; }
.btn-admin {
  background: rgba(255,255,255,0.12);
  color: #d4e4ff;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 10px;
  padding: 9px 16px;
  font-size: 13px;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
}
.btn-admin:hover { background: rgba(255,255,255,0.22); }

/* ── Body ─── */
.calc-body {
  max-width: 960px;
  margin: 28px auto;
  padding: 0 16px 80px;
}

/* ── Mode Tabs ─── */
.mode-tabs { display: flex; gap: 8px; margin-bottom: 20px; }
.mode-tab {
  padding: 10px 22px;
  border: 2px solid #dde3ef;
  border-radius: 10px;
  background: #fff;
  color: #6b7a99;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.mode-tab.active {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #1d4ed8;
}

/* ── AI Panel ─── */
.ai-panel { margin-bottom: 20px; }
.ai-upload-area {
  border: 2.5px dashed #c4cedf;
  border-radius: 16px;
  background: #fff;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s;
  overflow: hidden;
  cursor: pointer;
}
.ai-upload-area.drag-over { border-color: #3b82f6; background: #eff6ff; }
.ai-upload-placeholder { text-align: center; padding: 40px; color: #8fa0bb; }
.ai-upload-placeholder .ai-upload-icon { font-size: 56px; margin-bottom: 12px; }
.ai-upload-placeholder .link { color: #3b82f6; font-weight: 600; cursor: pointer; }
.ai-upload-placeholder small { display: block; margin-top: 8px; font-size: 12px; }
.ai-preview { width: 100%; max-height: 320px; position: relative; }
.ai-preview img { width: 100%; max-height: 320px; object-fit: cover; display: block; }
.btn-change-img {
  position: absolute; bottom: 12px; right: 12px;
  background: rgba(0,0,0,0.6); color: #fff;
  border: none; border-radius: 8px; padding: 6px 12px; cursor: pointer; font-size: 13px;
}
.hidden { display: none; }
.btn-analyze {
  width: 100%; margin-top: 12px;
  padding: 14px; border-radius: 12px;
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: #fff; border: none; font-size: 15px; font-weight: 700;
  cursor: pointer; transition: opacity 0.2s;
}
.btn-analyze:disabled { opacity: 0.6; cursor: not-allowed; }
.ai-result-box {
  margin-top: 14px;
  background: #f0fdf4; border: 1.5px solid #86efac;
  border-radius: 12px; padding: 16px;
}
.ai-result-header { display: flex; justify-content: space-between; align-items: center; font-weight: 700; margin-bottom: 6px; }
.ai-confidence.high { color: #16a34a; }
.ai-confidence.low { color: #d97706; }
.ai-notes { color: #4b5563; font-size: 14px; margin: 0 0 12px; }
.btn-apply-ai {
  width: 100%; padding: 10px; border-radius: 8px;
  background: #16a34a; color: #fff;
  border: none; font-size: 14px; font-weight: 600; cursor: pointer;
}

/* ── Step Cards ─── */
.constructor { display: flex; flex-direction: column; gap: 16px; }
.step-card {
  background: #fff;
  border-radius: 16px;
  padding: 22px 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.step-label {
  font-size: 15px; font-weight: 700; color: #1e293b;
  margin-bottom: 16px; display: flex; align-items: center; gap: 10px;
}
.step-num {
  width: 26px; height: 26px; border-radius: 50%;
  background: #3b82f6; color: #fff;
  font-size: 13px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

/* ── Type Cards ─── */
.type-grid { display: flex; gap: 12px; flex-wrap: wrap; }
.type-grid-2 { max-width: 350px; }
.type-card {
  flex: 1; min-width: 100px;
  border: 2.5px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafbfc;
}
.type-card:hover { border-color: #93c5fd; background: #f0f7ff; }
.type-card.selected { border-color: #3b82f6; background: #eff6ff; }
.type-icon { font-size: 32px; margin-bottom: 8px; }
.type-name { font-size: 13px; font-weight: 600; color: #334155; }

/* Direction icons */
.dir-icon { display: flex; align-items: center; justify-content: center; height: 40px; }
.dir-vertical { display: flex; flex-direction: column; gap: 3px; }
.dir-row { width: 44px; height: 12px; background: #3b82f6; border-radius: 3px; opacity: 0.7; }
.dir-horizontal { display: flex; flex-direction: row; gap: 3px; }
.dir-col { width: 12px; height: 40px; background: #3b82f6; border-radius: 3px; opacity: 0.7; }

/* ── Dims ─── */
.dims-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px; }
.dim-field { display: flex; flex-direction: column; gap: 6px; }
.dim-field label { font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.03em; }
.dim-field input {
  border: 2px solid #e2e8f0;
  border-radius: 9px;
  padding: 9px 12px;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  transition: border-color 0.2s;
  outline: none;
}
.dim-field input:focus { border-color: #3b82f6; }

/* Count control */
.count-control {
  display: flex; align-items: center;
  border: 2px solid #e2e8f0; border-radius: 9px;
  overflow: hidden;
}
.count-control button {
  width: 36px; height: 38px; border: none;
  background: #f1f5f9; color: #334155;
  font-size: 20px; font-weight: 700; cursor: pointer;
  transition: background 0.2s;
}
.count-control button:hover { background: #dbeafe; }
.count-control span { flex: 1; text-align: center; font-size: 17px; font-weight: 700; color: #1e293b; }

/* ── Box Preview ─── */
.box-preview { margin-top: 20px; display: flex; flex-direction: column; align-items: center; gap: 8px; }
.box-preview-cabinet {
  background: #d4a76a;
  border: 3px solid #9b6f3a;
  border-radius: 6px;
  padding: 4px;
  gap: 3px;
  flex-wrap: nowrap;
  overflow: hidden;
  transition: all 0.3s;
}
.box-preview-drawer {
  flex: 1;
  background: #e8c990;
  border-radius: 3px;
  border: 2px solid #b5892a;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 20px;
}
.drawer-facade { font-size: 12px; color: #7a4d0a; }
.box-preview-label { font-size: 12px; color: #64748b; font-weight: 600; }

/* ── Selects ─── */
.select-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 14px; margin-bottom: 16px; }
.select-field { display: flex; flex-direction: column; gap: 6px; }
.select-field label { font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.03em; }
.select-field select {
  border: 2px solid #e2e8f0; border-radius: 9px;
  padding: 9px 12px; font-size: 14px; color: #1e293b;
  background: #fff; outline: none; cursor: pointer;
  transition: border-color 0.2s;
}
.select-field select:focus { border-color: #3b82f6; }

.services-list { padding-top: 4px; }
.services-label { font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 10px; }
.service-checkboxes { display: flex; flex-wrap: wrap; gap: 10px; }
.service-check {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; color: #334155; cursor: pointer;
  padding: 6px 12px; border-radius: 8px; border: 1.5px solid #e2e8f0;
  transition: all 0.2s;
}
.service-check:hover { border-color: #93c5fd; }
.service-check input[type="checkbox"] { width: 16px; height: 16px; accent-color: #3b82f6; }

/* ── Calculate Button ─── */
.btn-calculate {
  width: 100%; padding: 17px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff; border: none; border-radius: 14px;
  font-size: 17px; font-weight: 800; cursor: pointer;
  box-shadow: 0 6px 20px rgba(37,99,235,0.35);
  transition: all 0.2s; margin-top: 8px;
}
.btn-calculate:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(37,99,235,0.45); }
.btn-calculate:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

/* ── Results ─── */
.results-panel {
  margin-top: 28px; background: #fff;
  border-radius: 16px; padding: 28px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.1);
  border-top: 4px solid #3b82f6;
}
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.results-header h2 { margin: 0; font-size: 20px; color: #1e293b; }
.results-actions { display: flex; gap: 10px; }
.btn-save, .btn-print {
  padding: 8px 16px; border-radius: 9px;
  font-size: 13px; font-weight: 600; cursor: pointer; border: 2px solid;
  transition: all 0.2s;
}
.btn-save { background: #10b981; border-color: #10b981; color: #fff; }
.btn-print { background: #fff; border-color: #cbd5e1; color: #475569; }
.btn-print:hover { border-color: #3b82f6; }

.result-summary-box {
  background: #eff6ff; border-radius: 10px; padding: 12px 16px;
  margin-bottom: 16px; font-size: 14px; color: #1e40af; font-weight: 600;
}

.details-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 20px; }
.details-table thead tr { background: #f8fafc; }
.details-table th { padding: 10px 12px; text-align: left; color: #64748b; font-weight: 700; font-size: 11px; text-transform: uppercase; border-bottom: 2px solid #e2e8f0; }
.details-table td { padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #334155; }
.details-table tbody tr:hover { background: #f8fafc; }
.mat-cell { color: #64748b; font-size: 12px; }
.dim-cell { font-family: monospace; color: #475569; }
.qty-cell { font-weight: 700; }
.price-cell { font-weight: 700; color: #1d4ed8; text-align: right; }

.totals-grid { display: flex; flex-direction: column; gap: 6px; max-width: 320px; margin-left: auto; }
.total-row { display: flex; justify-content: space-between; font-size: 14px; color: #334155; padding: 6px 0; border-bottom: 1px solid #f1f5f9; }
.total-row.grand { padding-top: 12px; border-top: 2px solid #1d4ed8; border-bottom: none; font-size: 18px; color: #1e293b; margin-top: 4px; }
.total-row.grand strong { color: #1d4ed8; font-size: 22px; }

/* ── Toast ─── */
.toast {
  position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
  padding: 12px 24px; border-radius: 10px; color: #fff;
  font-size: 14px; font-weight: 600; z-index: 9999;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  animation: slideUp 0.3s ease;
}
.toast.success { background: #10b981; }
.toast.error { background: #ef4444; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

/* ── Print ─── */
@media print {
  .calc-header, .mode-tabs, .ai-panel, .constructor, .btn-save, .btn-print, .toast { display: none !important; }
  .results-panel { box-shadow: none; border: 1px solid #ccc; }
}

/* ── Mobile ─── */
@media (max-width: 640px) {
  .calc-header-inner { flex-direction: column; gap: 12px; text-align: center; }
  .mode-tabs { flex-direction: column; }
  .type-grid { flex-direction: column; }
  .dims-grid { grid-template-columns: 1fr 1fr; }
  .select-grid { grid-template-columns: 1fr; }
  .results-actions { flex-direction: column; }
  .details-table { font-size: 11px; }
  .details-table th, .details-table td { padding: 7px 6px; }
}
</style>
