<template>
  <div class="attendance-container">
    <!-- 1. Top Statistics Section -->
    <div class="stats-overview">
      <div class="stats-header">
        <h2>{{ currentMonthTitle }} — {{ selectedDepartmentName }}</h2>
        <div class="month-nav">
          <el-button :icon="ArrowLeft" circle @click="moveMonth(-1)" />
          <span class="month-display">{{ currentMonthTitle }}</span>
          <el-button :icon="ArrowRight" circle @click="moveMonth(1)" />
        </div>
      </div>
      
      <el-row :gutter="20" class="mt-4">
        <el-col :span="4">
          <div class="stat-card">
            <span class="stat-label">Робочих днів</span>
            <span class="stat-value">{{ workingDaysCount }}</span>
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-card">
            <span class="stat-label">Середня явка</span>
            <span class="stat-value">{{ avgAttendance }}%</span>
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-card highlight-danger">
            <span class="stat-label">Пропуски без причини (!)</span>
            <span class="stat-value">{{ totalAbsencesWithoutReason }}</span>
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-card highlight-warning">
            <span class="stat-label">На лікарняному зараз</span>
            <span class="stat-value">{{ currentSickCount }}</span>
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-card highlight-info">
            <span class="stat-label">У відпустці зараз</span>
            <span class="stat-value">{{ currentVacationCount }}</span>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 2. Controls and Legend -->
    <div class="header-card mt-4">
      <div class="controls-left">
        <el-select 
          v-model="filterDepartment" 
          placeholder="Оберіть підрозділ" 
          clearable 
          @change="fetchData"
          style="width: 200px"
        >
          <el-option
            v-for="dept in departments"
            :key="dept.id"
            :label="dept.name"
            :value="dept.id"
          />
        </el-select>
        
        <el-button :icon="MagicStick" type="warning" plain @click="confirmBulkFill">
          Заповнити місяць (авто П/В)
        </el-button>
      </div>
      
      <div class="legend">
        <div v-for="status in statusList" :key="status.code" class="legend-item">
          <span class="status-box" :style="{ backgroundColor: status.color }">{{ status.code }}</span>
          <span class="status-label">{{ status.label }}</span>
        </div>
      </div>

      <div class="actions">
        <el-button type="primary" :loading="saving" :icon="Check" @click="saveChanges" size="large">
          Зберегти зміни
        </el-button>
      </div>
    </div>

    <!-- 3. Attendance Grid -->
    <el-card class="grid-card mt-4" v-loading="loading">
      <div class="grid-wrapper">
        <table class="attendance-table">
          <thead>
            <tr>
              <th class="sticky-col name-col">Співробітник</th>
              <th v-for="day in daysInMonth" :key="day" :class="{ 'is-weekend': isHolidayOrWeekend(day) }">
                <el-tooltip 
                  v-if="getHolidayName(day)" 
                  :content="getHolidayName(day)" 
                  placement="top"
                >
                  <div class="day-header-content">
                    <div class="day-num">{{ day }}</div>
                    <div class="day-week">{{ getDayOfWeek(day) }}</div>
                  </div>
                </el-tooltip>
                <div v-else class="day-header-content">
                  <div class="day-num">{{ day }}</div>
                  <div class="day-week">{{ getDayOfWeek(day) }}</div>
                </div>
              </th>
              <th class="summary-col">Підсумок</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="emp in employees" :key="emp.id">
              <td class="sticky-col name-col">
                <div class="emp-info">
                  <span class="emp-name">{{ emp.full_name }}</span>
                  <span class="emp-pos">{{ emp.position }}</span>
                </div>
              </td>
              <td 
                v-for="day in daysInMonth" 
                :key="day" 
                :class="{ 
                  'is-weekend': isHolidayOrWeekend(day),
                  'is-modified': isDayModified(emp.id, day)
                }"
              >
                <!-- Status Picker Popover with Holiday Tooltip -->
                <el-tooltip 
                  :disabled="!getHolidayName(day)" 
                  :content="getHolidayName(day)" 
                  placement="top"
                >
                  <el-popover placement="bottom" :width="180" trigger="click">
                    <template #reference>
                      <div class="status-cell" :style="{ backgroundColor: getCellColor(emp.id, day) }">
                        {{ getCellText(emp.id, day) }}
                      </div>
                    </template>
                    <div class="status-picker">
                      <div 
                        v-for="status in statusList" 
                        :key="status.code" 
                        class="picker-option"
                        :style="{ backgroundColor: status.color }"
                        @click="setAttendance(emp.id, day, status)"
                      >
                        {{ status.code }} - {{ status.label }}
                      </div>
                      <div class="picker-option clear-opt" @click="setAttendance(emp.id, day, null)">
                        Очистити
                      </div>
                    </div>
                  </el-popover>
                </el-tooltip>
              </td>
              <td class="summary-col">
                <div class="row-stats">
                  <span class="stat-p">Р: {{ getRowStats(emp.id).P }}</span>
                  <span class="stat-v">В: {{ getRowStats(emp.id).V }}</span>
                  <span class="stat-l">Х: {{ getRowStats(emp.id).L }}</span>
                </div>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="footer-summary">
              <td class="sticky-col name-col">Явка</td>
              <td v-for="day in daysInMonth" :key="day">
                {{ getColumnStats(day) }}
              </td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, ArrowRight, MagicStick, Check } from '@element-plus/icons-vue'
import api from '@/api'
import dayjs from 'dayjs'
import 'dayjs/locale/uk'

dayjs.locale('uk')

// 1. App State
const selectedMonth = ref(dayjs())
const filterDepartment = ref(null)
const loading = ref(false)
const saving = ref(false)

const employees = ref([])
const departments = ref([])
const holidayList = ref([]) // From DB
const attendanceData = ref([])
const modifiedRecords = ref({}) // { "empId_day": statusObject }

// 2. Constants / Dictionaries
const statusList = [
  { code: 'П', label: 'Працював', color: '#67C23A', saId: null }, // Green
  { code: 'В', label: 'Вихідний', color: '#909399', saId: null }, // Grey
  { code: 'Л', label: 'Лікарняний', color: '#E6A23C', saId: null }, // Yellow
  { code: 'ВП', label: 'Відпустка', color: '#409EFF', saId: null }, // Blue
  { code: '!', label: 'Без причини', color: '#F56C6C', saId: null }  // Red
]

// 3. Computed Helpers
const currentMonthTitle = computed(() => {
  return selectedMonth.value.format('MMMM YYYY')
})

const selectedDepartmentName = computed(() => {
  const dept = departments.value.find(d => d.id === filterDepartment.value)
  return dept ? dept.name : 'Всі підрозділи'
})

const daysInMonth = computed(() => selectedMonth.value.daysInMonth())

const isHolidayOrWeekend = (day) => {
  const dateStr = selectedMonth.value.date(day).format('YYYY-MM-DD')
  const isHoliday = holidayList.value.some(h => h.code === dateStr)
  if (isHoliday) return true
  
  const dow = selectedMonth.value.date(day).day()
  return dow === 0 || dow === 6 // Sun or Sat
}

const getDayOfWeek = (day) => selectedMonth.value.date(day).format('dd')

const getHolidayName = (day) => {
  const dateStr = selectedMonth.value.date(day).format('YYYY-MM-DD')
  const holiday = holidayList.value.find(h => h.code === dateStr)
  return holiday ? holiday.name : null
}

// 4. Working with records
const getRecord = (empId, day) => {
  const key = `${empId}_${day}`
  if (modifiedRecords.value[key] !== undefined) {
    const mod = modifiedRecords.value[key]
    return mod ? { status_code: mod.code } : null
  }
  const dbRec = attendanceData.value.find(r => 
    r.employee_id === empId && dayjs(r.date).date() === day
  )
  if (dbRec) {
    return { status_code: dbRec.status_name }
  }
  return null
}

const getCellText = (empId, day) => {
  const rec = getRecord(empId, day)
  return rec ? rec.status_code : ''
}

const getCellColor = (empId, day) => {
  const rec = getRecord(empId, day)
  if (!rec) return 'transparent'
  const status = statusList.find(s => s.code === rec.status_code)
  return status ? status.color : 'transparent'
}

const isDayModified = (empId, day) => modifiedRecords.value[`${empId}_${day}`] !== undefined

const setAttendance = (empId, day, status) => {
  modifiedRecords.value[`${empId}_${day}`] = status
}

// 5. Statistics Calculations
const workingDaysCount = computed(() => {
  let count = 0
  for (let d = 1; d <= daysInMonth.value; d++) {
    if (!isHolidayOrWeekend(d)) count++
  }
  return count
})

const avgAttendance = computed(() => {
  if (employees.value.length === 0) return 0
  let totalPresent = 0
  let totalPossible = employees.value.length * workingDaysCount.value
  
  employees.value.forEach(emp => {
    for (let d = 1; d <= daysInMonth.value; d++) {
      if (isHolidayOrWeekend(d)) continue
      const txt = getCellText(emp.id, d)
      if (txt === 'П') totalPresent++
    }
  })
  return totalPossible > 0 ? Math.round((totalPresent / totalPossible) * 100) : 0
})

const totalAbsencesWithoutReason = computed(() => {
  let count = 0
  employees.value.forEach(emp => {
    for (let d = 1; d <= daysInMonth.value; d++) {
      if (getCellText(emp.id, d) === '!') count++
    }
  })
  return count
})

const currentSickCount = computed(() => {
  let count = 0
  const today = dayjs().date()
  employees.value.forEach(emp => {
    if (getCellText(emp.id, today) === 'Л') count++
  })
  return count
})

const currentVacationCount = computed(() => {
  let count = 0
  const today = dayjs().date()
  employees.value.forEach(emp => {
    if (getCellText(emp.id, today) === 'ВП') count++
  })
  return count
})

const getRowStats = (empId) => {
  const stats = { P: 0, V: 0, L: 0 }
  for (let d = 1; d <= daysInMonth.value; d++) {
    const txt = getCellText(empId, d)
    if (txt === 'П') stats.P++
    else if (txt === 'В') stats.V++
    else if (txt === 'Л') stats.L++
  }
  return stats
}

const getColumnStats = (day) => {
  if (employees.value.length === 0) return '0/0'
  let present = 0
  employees.value.forEach(emp => {
    if (getCellText(emp.id, day) === 'П') present++
  })
  return `${present}/${employees.value.length}`
}

// 6. Data Fetching
const fetchData = async () => {
  loading.value = true
  try {
    // 1. Fetch holidays and depts
    const [deptRes, holidayRes, statusRes] = await Promise.all([
      api.get('/api/v1/departments'),
      api.get('/api/v1/dictionaries/items?type=HOLIDAY'),
      api.get('/api/v1/dictionaries/items?type=ATTENDANCE_STATUS')
    ])
    departments.value = deptRes.data
    holidayList.value = holidayRes.data.map(h => ({ ...h, code: h.code || '' }))
    
    // Map status names to IDs for backend saving
    statusList.forEach(s => {
      const match = statusRes.data.find(db => db.code === s.code)
      if (match) s.saId = match.id
    })

    // 2. Fetch Employees
    const empParams = { department_id: filterDepartment.value || undefined, limit: 200 }
    const empRes = await api.get('/api/v1/employees', { params: empParams })
    employees.value = empRes.data

    // 3. Fetch Attendance
    const start = selectedMonth.value.startOf('month').format('YYYY-MM-DD')
    const end = selectedMonth.value.endOf('month').format('YYYY-MM-DD')
    const attRes = await api.get('/api/v1/attendance', {
      params: { start_date: start, end_date: end }
    })
    attendanceData.value = attRes.data
    modifiedRecords.value = {}
  } catch (err) {
    console.error(err)
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

// 7. Actions
const moveMonth = (delta) => {
  selectedMonth.value = selectedMonth.value.add(delta, 'month')
  fetchData()
}

const confirmBulkFill = () => {
  ElMessageBox.confirm(
    'Заповнити всі порожні комірки місяця? Будні будуть встановлені як "П", вихідні як "В". Існуючі записи не зміняться.',
    'Масове заповнення',
    { confirmButtonText: 'Заповнити', cancelButtonText: 'Скасувати' }
  ).then(() => {
    const presentStatus = statusList.find(s => s.code === 'П')
    const weekendStatus = statusList.find(s => s.code === 'В')

    employees.value.forEach(emp => {
      for (let d = 1; d <= daysInMonth.value; d++) {
        if (!getCellText(emp.id, d)) {
          if (isHolidayOrWeekend(d)) {
            setAttendance(emp.id, d, weekendStatus)
          } else {
            setAttendance(emp.id, d, presentStatus)
          }
        }
      }
    })
    ElMessage.success('Місяць автоматично заповнено')
  })
}

const saveChanges = async () => {
  const toSave = []
  for (const [key, status] of Object.entries(modifiedRecords.value)) {
    const [empId, day] = key.split('_')
    if (status === null) continue 
    
    toSave.push({
      employee_id: empId,
      date: selectedMonth.value.date(parseInt(day)).format('YYYY-MM-DD'),
      status_id: status.saId
    })
  }

  if (toSave.length === 0) {
    ElMessage.info('Немає змін для збереження')
    return
  }

  saving.value = true
  try {
    await api.post('/api/v1/attendance/upsert', { records: toSave })
    ElMessage.success('Дані збережено успішно')
    fetchData()
  } catch (err) {
    ElMessage.error('Помилка збереження')
  } finally {
    saving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.attendance-container {
  padding: 24px;
  background-color: #f8f9fa;
  min-height: calc(100vh - 64px);
}

/* Statistics Styles */
.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #1a1d1f;
}

.month-nav {
  display: flex;
  align-items: center;
  gap: 15px;
  background: white;
  padding: 5px 15px;
  border-radius: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.month-display {
  font-weight: 600;
  min-width: 140px;
  text-align: center;
  text-transform: capitalize;
}

.stat-card {
  background: white;
  padding: 16px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}

.stat-label {
  font-size: 12px;
  color: #6f767e;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #1a1d1f;
}

.highlight-danger .stat-value { color: #F56C6C; }
.highlight-warning .stat-value { color: #E6A23C; }
.highlight-info .stat-value { color: #409EFF; }

/* Grid Styles */
.header-card {
  background: white;
  padding: 16px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.controls-left {
  display: flex;
  gap: 12px;
}

.legend {
  display: flex;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.status-box {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 11px;
}

.grid-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.grid-wrapper {
  overflow: auto;
  max-width: 100%;
}

.attendance-table {
  border-collapse: collapse;
  width: 100%;
  table-layout: fixed;
}

.attendance-table th, 
.attendance-table td {
  border: 1px solid #efefef;
  text-align: center;
  padding: 0;
  width: 45px;
  height: 50px;
}

.attendance-table th {
  background: #fcfcfc;
  font-size: 11px;
  color: #6f767e;
}

.day-num { font-size: 14px; font-weight: 700; }
.day-week { font-size: 10px; text-transform: uppercase; }

.attendance-table .name-col {
  width: 220px;
  text-align: left;
  padding: 8px 15px;
}

.attendance-table .summary-col {
  width: 120px;
  background: #f9fafb;
}

.sticky-col {
  position: sticky;
  left: 0;
  background: white;
  z-index: 2;
  box-shadow: 2px 0 5px rgba(0,0,0,0.02);
}

.emp-info {
  display: flex;
  flex-direction: column;
}

.emp-name {
  font-weight: 600;
  font-size: 14px;
  color: #1a1d1f;
}

.emp-pos {
  font-size: 11px;
  color: #6f767e;
}

.is-weekend {
  background-color: #f5f5f5 !important;
}

.status-cell {
  width: 100%;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  font-weight: bold;
  font-size: 15px;
  transition: all 0.2s;
}

.status-cell:hover {
  filter: brightness(0.9);
}

.is-modified {
  background-color: #fff9db !important;
}

.row-stats {
  display: flex;
  gap: 8px;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
}

.stat-p { color: #67C23A; }
.stat-v { color: #909399; }
.stat-l { color: #E6A23C; }

.footer-summary {
  background: #f9fafb;
  font-weight: 700;
  font-size: 12px;
}

.status-picker {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.picker-option {
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  color: white;
  font-weight: 600;
  font-size: 12px;
  transition: transform 0.1s;
}

.picker-option:hover {
  transform: scale(1.02);
}

.clear-opt {
  background: #f4f4f5;
  color: #606266;
  text-align: center;
}

.mt-4 { margin-top: 16px; }
</style>
