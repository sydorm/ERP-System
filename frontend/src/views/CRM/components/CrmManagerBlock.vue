<template>
  <div class="manager-selection-wrapper">
    <div v-if="!canReassignManager" class="manager-display-only">
      <div class="manager-avatar-mini">{{ initials(selectedManagerName) }}</div>
      <div class="manager-text">
        <span class="name">{{ selectedManagerName }}</span>
        <span class="role">Відповідальний</span>
      </div>
      <span class="manager-live-dot" />
    </div>
    <el-select
      v-else
      v-model="form.manager_id"
      filterable
      placeholder="Оберіть менеджера"
      class="premium-manager-select"
    >
      <template #prefix v-if="selectedManager">
        <div class="manager-avatar-mini prefix-avatar">
          {{ initials(selectedManagerName) }}
        </div>
      </template>
      <el-option
        v-for="u in normalizedManagerOptions"
        :key="u.id"
        :label="u.name"
        :value="u.id"
      >
        <div class="manager-option-item">
          <div class="manager-avatar-mini">{{ initials(u.name) }}</div>
          <div class="manager-info-stack">
            <span class="name">{{ u.name }}</span>
            <span class="role">Менеджер</span>
          </div>
        </div>
      </el-option>
    </el-select>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  form: { type: Object, required: true },
  managerOptions: { type: Array, required: true },
  canReassignManager: { type: Boolean, default: false },
})

const getUserName = (u) => (
  u?.name
  || u?.full_name
  || [u?.firstName || u?.first_name, u?.lastName || u?.last_name].filter(Boolean).join(' ')
  || u?.email
  || u?.username
  || 'Менеджер'
)

const initials = (name) => {
  if (!name) return 'М'
  const words = name.split(/\s+/).filter(Boolean)
  return words.slice(0, 2).map(word => word[0]).join('').toUpperCase() || 'М'
}

const normalizedManagerOptions = computed(() => (
  props.managerOptions.map(u => ({ ...u, name: getUserName(u) }))
))

const selectedManager = computed(() => (
  normalizedManagerOptions.value.find(u => String(u.id) === String(props.form.manager_id))
))

const selectedManagerName = computed(() => selectedManager.value?.name || 'Поточний користувач')
</script>

<style scoped>
.manager-selection-wrapper {
  width: 100%;
}

.manager-display-only {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 40px;
  padding: 5px 10px 5px 6px;
  background:
    linear-gradient(90deg, #F8FAFF, #FFFFFF);
  border: 1px solid #E0E7FF;
  border-radius: 14px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.9);
}

.manager-avatar-mini {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #7C3AED 0%, #1463FF 100%);
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 800;
  flex-shrink: 0;
  box-shadow: 0 8px 14px rgba(99, 102, 241, 0.22);
}

.manager-text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.manager-text .name {
  font-size: 13px;
  font-weight: 850;
  color: #1E293B;
}

.manager-text .role {
  font-size: 9px;
  color: #6366F1;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.manager-live-dot {
  width: 8px;
  height: 8px;
  margin-left: auto;
  border-radius: 999px;
  background: #15B97A;
  box-shadow: 0 0 0 4px rgba(21, 185, 122, .12);
}

.premium-manager-select {
  width: 100%;
}

:deep(.el-select__wrapper) {
  min-height: 40px !important;
  padding-left: 8px !important;
  border-radius: 14px !important;
  background: linear-gradient(90deg, #F8FAFF, #FFFFFF) !important;
  border: 1px solid #E0E7FF !important;
  box-shadow: none !important;
  transition: border-color .18s ease, box-shadow .18s ease;
}

:deep(.el-select__wrapper:hover),
:deep(.el-select__wrapper.is-focused) {
  border-color: #6366F1 !important;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, .06) !important;
}

.prefix-avatar {
  margin-right: 8px;
}

.manager-option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 0;
}

.manager-info-stack {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.manager-info-stack .name {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
}

.manager-info-stack .role {
  font-size: 10px;
  color: #94A3B8;
}

:deep(.el-select__prefix) {
  display: flex;
  align-items: center;
}
</style>
