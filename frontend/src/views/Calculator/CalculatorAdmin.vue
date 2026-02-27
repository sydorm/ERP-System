<template>
  <div class="admin-root">
    <div class="admin-header">
      <div class="admin-header-inner">
        <div class="admin-logo">
          <span>⚙️</span>
          <div>
            <h1>Налаштування калькулятора</h1>
            <p>Управління цінами на матеріали, фурнітуру і послуги</p>
          </div>
        </div>
        <a href="/calculator" class="btn-back">← Повернутись до конструктора</a>
      </div>
    </div>

    <div class="admin-body">
      <!-- Tabs -->
      <div class="tabs">
        <button :class="['tab', { active: tab === 'materials' }]" @click="tab = 'materials'">
          🪵 Матеріали ({{ materials.length }})
        </button>
        <button :class="['tab', { active: tab === 'hardware' }]" @click="tab = 'hardware'">
          ⚙️ Фурнітура ({{ hardware.length }})
        </button>
        <button :class="['tab', { active: tab === 'services' }]" @click="tab = 'services'">
          🔨 Послуги ({{ services.length }})
        </button>
      </div>

      <!-- ── Materials ── -->
      <div v-if="tab === 'materials'" class="panel">
        <div class="panel-header">
          <h2>Матеріали</h2>
          <button class="btn-add" @click="openAdd('materials')">+ Додати</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Назва</th><th>Товщина</th><th>Ціна / м²</th><th>Статус</th><th></th></tr></thead>
            <tbody>
              <tr v-for="m in materials" :key="m.id">
                <td>{{ m.name }}</td>
                <td>{{ m.thickness_mm ? m.thickness_mm + 'мм' : '—' }}</td>
                <td class="price-cell">{{ m.price_per_m2 }} грн</td>
                <td><span :class="['badge', m.is_active ? 'active' : 'inactive']">{{ m.is_active ? 'Активний' : 'Вимкнений' }}</span></td>
                <td class="actions">
                  <button class="btn-edit" @click="openEdit('materials', m)">✏️</button>
                  <button class="btn-toggle" @click="toggleActive('materials', m)">{{ m.is_active ? '🔴' : '🟢' }}</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ── Hardware ── -->
      <div v-if="tab === 'hardware'" class="panel">
        <div class="panel-header">
          <h2>Фурнітура</h2>
          <button class="btn-add" @click="openAdd('hardware')">+ Додати</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Назва</th><th>Бренд</th><th>Довжина</th><th>Категорія</th><th>Ціна / {{ 'пара' }}</th><th>Статус</th><th></th></tr></thead>
            <tbody>
              <tr v-for="h in hardware" :key="h.id">
                <td>{{ h.name }}</td>
                <td>{{ h.brand || '—' }}</td>
                <td>{{ h.length_mm ? h.length_mm + 'мм' : '—' }}</td>
                <td>{{ h.category }}</td>
                <td class="price-cell">{{ h.price_per_unit }} грн</td>
                <td><span :class="['badge', h.is_active ? 'active' : 'inactive']">{{ h.is_active ? 'Активна' : 'Вимкнена' }}</span></td>
                <td class="actions">
                  <button class="btn-edit" @click="openEdit('hardware', h)">✏️</button>
                  <button class="btn-toggle" @click="toggleActive('hardware', h)">{{ h.is_active ? '🔴' : '🟢' }}</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ── Services ── -->
      <div v-if="tab === 'services'" class="panel">
        <div class="panel-header">
          <h2>Послуги</h2>
          <button class="btn-add" @click="openAdd('services')">+ Додати</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Назва</th><th>Ціна</th><th>Одиниця</th><th>Статус</th><th></th></tr></thead>
            <tbody>
              <tr v-for="s in services" :key="s.id">
                <td>{{ s.name }}</td>
                <td class="price-cell">{{ s.price }} грн</td>
                <td>{{ s.unit }}</td>
                <td><span :class="['badge', s.is_active ? 'active' : 'inactive']">{{ s.is_active ? 'Активна' : 'Вимкнена' }}</span></td>
                <td class="actions">
                  <button class="btn-edit" @click="openEdit('services', s)">✏️</button>
                  <button class="btn-toggle" @click="toggleActive('services', s)">{{ s.is_active ? '🔴' : '🟢' }}</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ── Modal ── -->
    <div v-if="modal.show" class="modal-overlay" @click.self="modal.show = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ modal.isEdit ? 'Редагувати' : 'Додати' }}</h3>
          <button class="modal-close" @click="modal.show = false">✕</button>
        </div>
        <div class="modal-body">
          <!-- Materials fields -->
          <template v-if="tab === 'materials'">
            <div class="field"><label>Назва</label><input v-model="modal.data.name" /></div>
            <div class="field"><label>Товщина (мм)</label><input v-model.number="modal.data.thickness_mm" type="number" /></div>
            <div class="field"><label>Ціна за м²</label><input v-model.number="modal.data.price_per_m2" type="number" step="0.01" /></div>
            <div class="field"><label>Одиниця</label><input v-model="modal.data.unit" /></div>
          </template>
          <!-- Hardware fields -->
          <template v-if="tab === 'hardware'">
            <div class="field"><label>Назва</label><input v-model="modal.data.name" /></div>
            <div class="field"><label>Бренд</label><input v-model="modal.data.brand" /></div>
            <div class="field"><label>Довжина (мм)</label><input v-model.number="modal.data.length_mm" type="number" /></div>
            <div class="field"><label>Категорія</label>
              <select v-model="modal.data.category">
                <option value="направляючі">Направляючі</option>
                <option value="ручки">Ручки</option>
                <option value="петлі">Петлі</option>
                <option value="інше">Інше</option>
              </select>
            </div>
            <div class="field"><label>Ціна (грн)</label><input v-model.number="modal.data.price_per_unit" type="number" step="0.01" /></div>
            <div class="field"><label>Одиниця</label><input v-model="modal.data.unit" /></div>
          </template>
          <!-- Services fields -->
          <template v-if="tab === 'services'">
            <div class="field"><label>Назва</label><input v-model="modal.data.name" /></div>
            <div class="field"><label>Ціна (грн)</label><input v-model.number="modal.data.price" type="number" step="0.01" /></div>
            <div class="field"><label>Одиниця</label><input v-model="modal.data.unit" placeholder="шт, пог.м, год..." /></div>
          </template>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="modal.show = false">Скасувати</button>
          <button class="btn-save" :disabled="saving" @click="save">
            {{ saving ? 'Зберігаю...' : 'Зберегти' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="toast.show" :class="['toast', toast.type]">{{ toast.msg }}</div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const tab = ref('materials')
const materials = ref([])
const hardware = ref([])
const services = ref([])
const saving = ref(false)
const toast = reactive({ show: false, msg: '', type: 'success' })
const modal = reactive({ show: false, isEdit: false, id: null, data: {} })

onMounted(async () => {
  await Promise.all([load('materials'), load('hardware'), load('services')])
})

async function load(type) {
  const r = await fetch(`${API}/api/calculator/${type}?active_only=false`)
  const data = await r.json()
  if (type === 'materials') materials.value = data
  else if (type === 'hardware') hardware.value = data
  else services.value = data
}

function openAdd(type) {
  modal.isEdit = false
  modal.id = null
  modal.data = type === 'materials'
    ? { name: '', thickness_mm: 16, price_per_m2: 0, unit: 'м²' }
    : type === 'hardware'
    ? { name: '', brand: '', length_mm: null, category: 'направляючі', price_per_unit: 0, unit: 'пара' }
    : { name: '', price: 0, unit: 'шт' }
  modal.show = true
}

function openEdit(type, item) {
  modal.isEdit = true
  modal.id = item.id
  modal.data = { ...item }
  modal.show = true
}

async function save() {
  saving.value = true
  try {
    const type = tab.value
    const url = modal.isEdit
      ? `${API}/api/calculator/${type}/${modal.id}`
      : `${API}/api/calculator/${type}`
    const method = modal.isEdit ? 'PATCH' : 'POST'
    const r = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(modal.data)
    })
    if (!r.ok) { const e = await r.json(); throw new Error(e.detail) }
    modal.show = false
    await load(type)
    showToast('Збережено!', 'success')
  } catch (e) {
    showToast('Помилка: ' + e.message, 'error')
  } finally {
    saving.value = false
  }
}

async function toggleActive(type, item) {
  const field = type === 'hardware' ? 'is_active' : 'is_active'
  await fetch(`${API}/api/calculator/${type}/${item.id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_active: !item.is_active })
  })
  await load(type)
  showToast(item.is_active ? 'Вимкнено' : 'Увімкнено', 'success')
}

function showToast(msg, type = 'success') {
  toast.msg = msg; toast.type = type; toast.show = true
  setTimeout(() => (toast.show = false), 3000)
}
</script>

<style scoped>
.admin-root { min-height: 100vh; background: #f1f3f8; font-family: 'Inter', sans-serif; }
.admin-header { background: linear-gradient(135deg, #1a2332, #2d3f5e); padding: 0 24px; }
.admin-header-inner { max-width: 1100px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 18px 0; }
.admin-logo { display: flex; align-items: center; gap: 14px; }
.admin-logo span { font-size: 32px; }
.admin-logo h1 { margin: 0; font-size: 20px; color: #fff; font-weight: 700; }
.admin-logo p { margin: 2px 0 0; font-size: 12px; color: #9eb5d8; }
.btn-back { color: #d4e4ff; font-size: 13px; text-decoration: none; padding: 8px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.1); transition: background 0.2s; }
.btn-back:hover { background: rgba(255,255,255,0.2); }

.admin-body { max-width: 1100px; margin: 28px auto; padding: 0 16px 80px; }
.tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.tab { padding: 10px 20px; border: 2px solid #dde3ef; border-radius: 10px; background: #fff; color: #6b7a99; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.tab.active { border-color: #3b82f6; background: #eff6ff; color: #1d4ed8; }

.panel { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.panel-header h2 { margin: 0; font-size: 18px; color: #1e293b; }
.btn-add { background: #3b82f6; color: #fff; border: none; border-radius: 9px; padding: 9px 16px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.btn-add:hover { background: #2563eb; }

.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
thead tr { background: #f8fafc; }
th { padding: 10px 14px; text-align: left; color: #64748b; font-weight: 700; font-size: 11px; text-transform: uppercase; border-bottom: 2px solid #e2e8f0; white-space: nowrap; }
td { padding: 11px 14px; border-bottom: 1px solid #f1f5f9; color: #334155; }
tbody tr:hover { background: #f8fafc; }
.price-cell { font-weight: 700; color: #1d4ed8; }
.actions { display: flex; gap: 6px; }
.btn-edit, .btn-toggle { border: none; background: none; cursor: pointer; font-size: 16px; padding: 4px 6px; border-radius: 6px; transition: background 0.2s; }
.btn-edit:hover, .btn-toggle:hover { background: #f1f5f9; }
.badge { padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge.active { background: #dcfce7; color: #16a34a; }
.badge.inactive { background: #fef2f2; color: #dc2626; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 16px; width: 100%; max-width: 440px; padding: 28px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.modal-header h3 { margin: 0; font-size: 18px; color: #1e293b; }
.modal-close { background: none; border: none; font-size: 18px; cursor: pointer; color: #64748b; }
.modal-body { display: flex; flex-direction: column; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 5px; }
.field label { font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; }
.field input, .field select { border: 2px solid #e2e8f0; border-radius: 8px; padding: 9px 12px; font-size: 14px; outline: none; transition: border-color 0.2s; }
.field input:focus, .field select:focus { border-color: #3b82f6; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
.btn-cancel { background: #f1f5f9; color: #475569; border: none; border-radius: 8px; padding: 10px 18px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-save { background: #3b82f6; color: #fff; border: none; border-radius: 8px; padding: 10px 18px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-save:disabled { opacity: 0.6; }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); padding: 12px 24px; border-radius: 10px; color: #fff; font-size: 14px; font-weight: 600; z-index: 9999; }
.toast.success { background: #10b981; }
.toast.error { background: #ef4444; }

@media (max-width: 640px) {
  .admin-header-inner { flex-direction: column; gap: 10px; }
  .tabs { flex-direction: column; }
  td, th { padding: 8px; font-size: 12px; }
}
</style>
