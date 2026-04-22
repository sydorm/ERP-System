<template>
  <div class="attendance-container">
    <!-- Header with controls -->
    <div class="header-card">
      <div class="controls-left">
        <el-date-picker
          v-model="selectedMonth"
          type="month"
          placeholder="Оберіть місяць"
          :clearable="false"
          @change="fetchData"
        />
        <el-select 
          v-model="filterDepartment" 
          placeholder="Підрозділ" 
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
      </div>
      
      <div class="legend">
        <div v-for="status in attendanceStatuses" :key="status.id" class="legend-item">
          <span class="status-dot" :style="{ backgroundColor: getStatusColor(status.name) }"></span>
          <span class="status-label">{{ status.name }}</span>
        </div>
      </div>

      <div class="actions">
        <el-button type="primary" :loading="saving" @click="saveChanges">
          Зберегти зміни
        </el-button>
      </div>
    </div>

    <!-- Attendance Grid -->
    <el-card class="grid-card" v-loading="loading">
      <div class="grid-wrapper">
        <table class="attendance-table">
          <thead>
            <tr>
              <th class="sticky-col name-col">Співробітник</th>
              <th v-for="day in daysInMonth" :key="day" :class="{ 'is-weekend': isWeekend(day) }">
                {{ day }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="emp in employees" :key="emp.id">
              <td class="sticky-col name-col">
                <div class="emp-info">
                  <span class="emp-name">{{ emp.full_name }}</span>
                  <span class="emp-dept">{{ emp.department_name }}</span>
                </div>
              </td>
              <td 
                v-for="day in daysInMonth" 
                :key="day" 
                :class="{ 
                  'is-weekend': isWeekend(day),
                  'is-modified': isDayModified(emp.id, day)
                }"
              >
                <el-dropdown trigger="click" @command="(cmd) => setAttendance(emp.id, day, cmd)">
                  <div class="status-cell" :style="{ backgroundColor: getCellColor(emp.id, day) }">
                    {{ getCellText(emp.id, day) }}
                  </div>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="clear">Очистити</el-dropdown-item>
                      <el-dropdown-item 
                        v-for="status in attendanceStatuses" 
                        :key="status.id" 
                        :command="status.id"
                      >
                        {{ status.name }}
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import dayjs from 'dayjs'

const selectedMonth = ref(new Date())
const filterDepartment = ref(null)
const loading = ref(false)
const saving = ref(false)

const employees = ref([])
const departments = ref([])
const attendanceStatuses = ref([])
const attendanceData = ref([]) // Current DB state
const modifiedRecords = ref({}) // Format: { "empId_day": statusId }

const daysInMonth = computed(() => {
  return dayjs(selectedMonth.value).daysInMonth()
})

const isWeekend = (day) => {
  const d = dayjs(selectedMonth.value).date(day)
  return d.day() === 0 || d.day() === 6
}

const fetchData = async () => {
  loading.value = true
  try {
    // 1. Fetch Dictionaries & Departments if not yet
    if (attendanceStatuses.value.length === 0) {
      const dictRes = await api.get('/api/v1/dictionaries/items?type=ATTENDANCE_STATUS')
      attendanceStatuses.value = dictRes.data
    }
    if (departments.value.length === 0) {
      const deptRes = await api.get('/api/v1/departments')
      departments.value = deptRes.data
    }

    // 2. Fetch Employees
    const empRes = await api.get('/api/v1/employees', {
      params: { department_id: filterDepartment.value }
    })
    employees.value = empRes.data

    // 3. Fetch Attendance for month
    const start = dayjs(selectedMonth.value).startOf('month').format('YYYY-MM-DD')
    const end = dayjs(selectedMonth.value).endOf('month').format('YYYY-MM-DD')
    const attRes = await api.get('/api/v1/attendance', {
      params: { start_date: start, end_date: end, department_id: filterDepartment.value }
    })
    attendanceData.value = attRes.data
    modifiedRecords.value = {}
  } catch (e) {
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

const getRecord = (empId, day) => {
  const key = `${empId}_${day}`
  if (modifiedRecords.value[key] !== undefined) {
    return { status_id: modifiedRecords.value[key] }
  }
  return attendanceData.value.find(r => 
    r.employee_id === empId && dayjs(r.date).date() === day
  )
}

const getCellText = (empId, day) => {
  const record = getRecord(empId, day)
  if (!record || !record.status_id) return ''
  const status = attendanceStatuses.value.find(s => s.id === record.status_id)
  return status ? status.name : ''
}

const getStatusColor = (name) => {
  switch (name) {
    case 'П': return '#ecf5ff' // Blue-ish for present
    case 'В': return '#fef0f0' // Red-ish for weekend/off
    case 'Л': return '#fdf6ec' // Orange for sick
    case 'О': return '#f0f9eb' // Green for vacation
    default: return 'transparent'
  }
}

const getCellColor = (empId, day) => {
  const record = getRecord(empId, day)
  if (!record || !record.status_id) return 'transparent'
  const status = attendanceStatuses.value.find(s => s.id === record.status_id)
  return status ? getStatusColor(status.name) : 'transparent'
}

const isDayModified = (empId, day) => {
  return modifiedRecords.value[`${empId}_${day}`] !== undefined
}

const setAttendance = (empId, day, command) => {
  const key = `${empId}_${day}`
  if (command === 'clear') {
    modifiedRecords.value[key] = null
  } else {
    modifiedRecords.value[key] = command
  }
}

const saveChanges = async () => {
  const toSave = []
  for (const [key, statusId] of Object.entries(modifiedRecords.value)) {
    const [empId, day] = key.split('_')
    toSave.push({
      employee_id: empId,
      date: dayjs(selectedMonth.value).date(parseInt(day)).format('YYYY-MM-DD'),
      status_id: statusId // null means we should ideally delete or skip, but upsert handles it
    })
  }

  if (toSave.length === 0) {
    ElMessage.info('Немає змін для збереження')
    return
  }

  saving.value = true
  try {
    await api.post('/api/v1/attendance/upsert', { records: toSave })
    ElMessage.success('Зміни збережено')
    fetchData()
  } catch (e) {
    ElMessage.error('Помилка збереження')
  } finally {
    saving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.attendance-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.header-card {
  background: var(--el-bg-color);
  padding: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--el-box-shadow-light);
}

.controls-left {
  display: flex;
  gap: 12px;
}

.legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  border: 1px solid var(--el-border-color);
}

.grid-card {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
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
  border: 1px solid var(--el-border-color-lighter);
  text-align: center;
  padding: 0;
  width: 35px;
  height: 40px;
}

.attendance-table th {
  background: var(--el-fill-color-lighter);
  font-size: 12px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
}

.attendance-table .name-col {
  width: 200px;
  text-align: left;
  padding: 8px 12px;
}

.sticky-col {
  position: sticky;
  left: 0;
  background: var(--el-bg-color);
  z-index: 2;
  box-shadow: 2px 0 5px rgba(0,0,0,0.05);
}

.emp-info {
  display: flex;
  flex-direction: column;
}

.emp-name {
  font-weight: 500;
  font-size: 14px;
}

.emp-dept {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
}

.is-weekend {
  background-color: var(--el-fill-color-light) !important;
}

.status-cell {
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
  transition: all 0.2s;
}

.status-cell:hover {
  filter: brightness(0.95);
}

.is-modified .status-cell {
  box-shadow: inset 0 0 0 2px var(--el-color-primary-light-3);
}

.attendance-table tbody tr:hover td {
  background-color: var(--el-fill-color-extra-light);
}
</style>
