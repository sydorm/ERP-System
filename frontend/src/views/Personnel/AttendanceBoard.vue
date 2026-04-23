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
        <el-col :span="4">
          <div class="stat-card">
            <span class="stat-label">Відпрацьовано</span>
            <span class="stat-value">{{ totalActualHours }} год</span>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card">
            <span class="stat-label">Норма годин</span>
            <span class="stat-value">{{ totalWorkingHoursNorm }} год</span>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card" :class="{ 'highlight-danger': totalHoursDiff < 0 }">
            <span class="stat-label">Різниця</span>
            <span class="stat-value">{{ totalHoursDiff > 0 ? '+' : '' }}{{ totalHoursDiff }} год</span>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card">
            <span class="stat-label">Середня явка</span>
            <span class="stat-value">{{ avgAttendance }}%</span>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-card highlight-danger">
            <span class="stat-label">Пропуски (!)</span>
            <span class="stat-value">{{ totalAbsencesWithoutReason }}</span>
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
                  <div class="status-cell" :style="{ backgroundColor: getCellColor(emp.id, day) }" @click="openDetails(emp, day)">
                    {{ getCellText(emp.id, day) }}
                    <div v-if="getRecord(emp.id, day)?.actual_hours > 0" class="cell-hours">
                      {{ getRecord(emp.id, day).actual_hours }}
                    </div>
                  </div>
              </td>
              <td class="summary-col">
                  <div class="row-stats" v-if="employeeStats[emp.id]">
                    <div class="row-stats-top">
                      <span class="stat-p">П:{{ employeeStats[emp.id].P }}</span>
                      <span class="stat-v">В:{{ employeeStats[emp.id].V }}</span>
                      <span class="stat-l">Л:{{ employeeStats[emp.id].L }}</span>
                    </div>
                    <div class="row-stats-hours">
                      Год: {{ employeeStats[emp.id].hours }}/{{ workingDaysCount * 8 }}
                    </div>
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
    <!-- 4. Detailed Day Dialog -->
    <el-dialog
      v-model="detailsVisible"
      :title="`Деталі дня: ${detailsForm.employee_name} — ${detailsForm.date_display}`"
      width="400px"
      append-to-body
    >
      <div class="details-dialog-form">
        <el-form label-position="top">
          <el-form-item label="Статус">
            <el-radio-group v-model="detailsForm.status_id" class="status-radio-group">
              <el-radio-button 
                v-for="status in statusList" 
                :key="status.code" 
                :label="status.saId"
              >
                {{ status.code }}
              </el-radio-button>
            </el-radio-group>
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Початок">
                <el-time-select
                  v-model="detailsForm.start_time"
                  start="06:00"
                  step="00:15"
                  end="22:00"
                  placeholder="08:00"
                  @change="calculateHours"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Кінець">
                <el-time-select
                  v-model="detailsForm.end_time"
                  start="06:00"
                  step="00:15"
                  end="22:00"
                  placeholder="17:00"
                  @change="calculateHours"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Перерва (год)">
                <el-input-number 
                  v-model="detailsForm.break_hours" 
                  :precision="1" 
                  :step="0.5" 
                  :min="0" 
                  :max="4"
                  @change="calculateHours"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Відпрацьовано">
                <el-input-number 
                  v-model="detailsForm.actual_hours" 
                  :precision="1" 
                  :step="0.5" 
                  disabled
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Примітка">
            <el-input 
              v-model="detailsForm.notes" 
              type="textarea" 
              rows="2" 
              placeholder="Причина відсутності, запізнення тощо..."
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">Скасувати</el-button>
        <el-button type="primary" @click="saveDetails">Зберегти</el-button>
      </template>
    </el-dialog>
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

// 2. Dialog state
const detailsVisible = ref(false)
const detailsForm = ref({
  employee_id: null,
  employee_name: '',
  day: null,
  date_display: '',
  status_id: null,
  start_time: '08:00',
  end_time: '17:00',
  break_hours: 1.0,
  actual_hours: 8.0,
  notes: ''
})

// 2. Constants / Dictionaries
const statusList = [
  { code: 'П', label: 'Працював', color: '#67C23A', saId: null }, // Green
  { code: 'В', label: 'Вихідний', color: '#909399', saId: null }, // Grey
  { code: 'Л', label: 'Лікарняний', color: '#E6A23C', saId: null }, // Yellow
  { code: 'Вд', label: 'Відпустка', color: '#409EFF', saId: null }, // Blue
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
  
  // 1. Check local modifications first
  if (modifiedRecords.value[key] !== undefined) {
    return modifiedRecords.value[key]
  }
  
  // 2. Check persistent data from DB
  const dbRec = attendanceData.value.find(r => 
    r.employee_id === empId && dayjs(r.date).date() === day
  )
  
  if (dbRec) {
    // Backend might return Code (П) or Label (Працював). We need to ensure we return a Code.
    const status = statusList.find(s => s.code === dbRec.status_name || s.label === dbRec.status_name)
    return { 
      status_id: dbRec.status_id,
      status_code: status ? status.code : dbRec.status_name,
      start_time: dbRec.start_time,
      end_time: dbRec.end_time,
      break_hours: dbRec.break_hours,
      actual_hours: dbRec.actual_hours,
      notes: dbRec.notes
    }
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
  if (!status) {
    modifiedRecords.value[`${empId}_${day}`] = null
    return
  }
  
  const isWeekend = isHolidayOrWeekend(day)
  modifiedRecords.value[`${empId}_${day}`] = {
    status_id: status.saId,
    status_code: status.code,
    start_time: isWeekend ? null : '08:00',
    end_time: isWeekend ? null : '17:00',
    break_hours: isWeekend ? 0 : 1.0,
    actual_hours: isWeekend ? 0 : 8.0,
    notes: ''
  }
}

const openDetails = (emp, day) => {
  const rec = getRecord(emp.id, day)
  const isWeekend = isHolidayOrWeekend(day)
  
  detailsForm.value = {
    employee_id: emp.id,
    employee_name: emp.full_name,
    day: day,
    date_display: selectedMonth.value.date(day).format('DD MMMM'),
    status_id: rec?.status_id || (isWeekend ? statusList.find(s => s.code === 'В').saId : statusList.find(s => s.code === 'П').saId),
    start_time: rec?.start_time || (isWeekend ? null : '08:00'),
    end_time: rec?.end_time || (isWeekend ? null : '17:00'),
    break_hours: rec?.break_hours !== undefined ? parseFloat(rec.break_hours) : (isWeekend ? 0 : 1.0),
    actual_hours: rec?.actual_hours !== undefined ? parseFloat(rec.actual_hours) : (isWeekend ? 0 : 8.0),
    notes: rec?.notes || ''
  }
  detailsVisible.value = true
}

const calculateHours = () => {
  const status = statusList.find(s => s.saId === detailsForm.value.status_id)
  if (status && status.code !== 'П') {
    detailsForm.value.actual_hours = 0
    return
  }

  if (!detailsForm.value.start_time || !detailsForm.value.end_time) {
    detailsForm.value.actual_hours = 0
    return
  }

  const start = dayjs(`2000-01-01 ${detailsForm.value.start_time}`)
  const end = dayjs(`2000-01-01 ${detailsForm.value.end_time}`)
  
  let diff = end.diff(start, 'minute') / 60
  diff -= (detailsForm.value.break_hours || 0)
  
  detailsForm.value.actual_hours = Math.max(0, parseFloat(diff.toFixed(1)))
}

const saveDetails = () => {
  const status = statusList.find(s => s.saId === detailsForm.value.status_id)
  modifiedRecords.value[`${detailsForm.value.employee_id}_${detailsForm.value.day}`] = {
    status_id: detailsForm.value.status_id,
    status_code: status ? status.code : '?',
    start_time: detailsForm.value.start_time,
    end_time: detailsForm.value.end_time,
    break_hours: detailsForm.value.break_hours,
    actual_hours: detailsForm.value.actual_hours,
    notes: detailsForm.value.notes
  }
  detailsVisible.value = false
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
      const rec = getRecord(emp.id, d)
      if (rec && rec.status_code === 'П') totalPresent++
    }
  })
  return totalPossible > 0 ? Math.round((totalPresent / totalPossible) * 100) : 0
})

const totalActualHours = computed(() => {
  let total = 0
  employees.value.forEach(emp => {
    for (let d = 1; d <= daysInMonth.value; d++) {
      const rec = getRecord(emp.id, d)
      if (rec && rec.actual_hours) total += parseFloat(rec.actual_hours)
    }
  })
  return parseFloat(total.toFixed(1))
})

const totalWorkingHoursNorm = computed(() => {
  return employees.value.length * workingDaysCount.value * 8
})

const totalHoursDiff = computed(() => {
  return parseFloat((totalActualHours.value - totalWorkingHoursNorm.value).toFixed(1))
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
    if (getCellText(emp.id, today) === 'Вд') count++
  })
  return count
})

const employeeStats = computed(() => {
  const map = {}
  employees.value.forEach(emp => {
    const stats = { P: 0, V: 0, L: 0, hours: 0 }
    for (let d = 1; d <= daysInMonth.value; d++) {
      const rec = getRecord(emp.id, d)
      if (!rec) continue
      
      if (rec.status_code === 'П') stats.P++
      else if (rec.status_code === 'В') stats.V++
      else if (rec.status_code === 'Л') stats.L++
      
      if (rec.actual_hours) stats.hours += parseFloat(rec.actual_hours)
    }
    map[emp.id] = stats
  })
  return map
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
  if (employees.value.length === 0) return '0%'
  let present = 0
  employees.value.forEach(emp => {
    if (getCellText(emp.id, day) === 'П') present++
  })
  return Math.round((present / employees.value.length) * 100) + '%'
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
      status_id: status.status_id,
      start_time: status.start_time,
      end_time: status.end_time,
      break_hours: status.break_hours,
      actual_hours: status.actual_hours,
      notes: status.notes
    })
  }

  if (toSave.length === 0) {
    ElMessage.info('Немає змін для збереження')
    return
  }

  saving.value = true
  try {
    await api.post('/api/v1/attendance/upsert', { records: toSave })
    
    // Optimistic Update: Move modified records to permanent attendanceData locally
    for (const [key, status] of Object.entries(modifiedRecords.value)) {
      if (!status) continue
      const [empId, dayStr] = key.split('_')
      const day = parseInt(dayStr)
      const date = selectedMonth.value.date(day).format('YYYY-MM-DD')
      
      const existingIdx = attendanceData.value.findIndex(r => 
        r.employee_id === empId && dayjs(r.date).isSame(date, 'day')
      )
      
      if (existingIdx > -1) {
        attendanceData.value[existingIdx].status_name = status.status_code
        attendanceData.value[existingIdx].status_id = status.status_id
        attendanceData.value[existingIdx].start_time = status.start_time
        attendanceData.value[existingIdx].end_time = status.end_time
        attendanceData.value[existingIdx].break_hours = status.break_hours
        attendanceData.value[existingIdx].actual_hours = status.actual_hours
        attendanceData.value[existingIdx].notes = status.notes
      } else {
        attendanceData.value.push({
          employee_id: empId,
          date: date,
          status_name: status.status_code,
          status_id: status.status_id,
          start_time: status.start_time,
          end_time: status.end_time,
          break_hours: status.break_hours,
          actual_hours: status.actual_hours,
          notes: status.notes
        })
      }
    }
    
    modifiedRecords.value = {}
    ElMessage.success('Дані збережено успішно')
    // No need for fetchData() anymore as we updated local state
  } catch (err) {
    console.error(err)
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
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  font-weight: bold;
  font-size: 14px;
  transition: all 0.2s;
  position: relative;
}

.cell-hours {
  font-size: 9px;
  opacity: 0.9;
  margin-top: -2px;
}

.status-cell:hover {
  filter: brightness(0.9);
}

.is-modified {
  background-color: #fff9db !important;
}

.row-stats {
  display: flex;
  flex-direction: column;
  gap: 2px;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  padding: 4px;
}

.row-stats-top {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.row-stats-hours {
  color: #1a1d1f;
  font-size: 10px;
  border-top: 1px solid #efefef;
  padding-top: 2px;
}

.stat-p { color: #2d661c; }
.stat-v { color: #4b5563; }
.stat-l { color: #92400e; }

.footer-summary {
  background: #f9fafb;
  font-weight: 700;
  font-size: 12px;
}

.details-dialog-form {
  padding: 10px 0;
}

.status-radio-group {
  width: 100%;
  display: flex;
  justify-content: space-between;
}

.status-radio-group :deep(.el-radio-button__inner) {
  width: 60px;
  padding: 8px 0;
}

.mt-4 { margin-top: 16px; }
</style>
