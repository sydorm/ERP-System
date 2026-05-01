<template>
  <div class="crm-field manager-field">
    <label class="crm-label">Відповідальний менеджер</label>
    <div v-if="!canReassignManager" class="manager-readonly">
      <span class="manager-avatar">{{ managerInitials }}</span>
      <span class="manager-info">
        <b>{{ selectedManagerName }}</b>
      </span>
    </div>
    <el-select
      v-else
      v-model="form.manager_id"
      filterable
      placeholder="Оберіть менеджера"
      class="manager-select"
    >
      <el-option
        v-for="u in normalizedManagerOptions"
        :key="u.id"
        :label="u.name"
        :value="u.id"
      />
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

const normalizedManagerOptions = computed(() => (
  props.managerOptions.map(u => ({ ...u, name: getUserName(u) }))
))

const selectedManager = computed(() => (
  normalizedManagerOptions.value.find(u => String(u.id) === String(props.form.manager_id))
))

const selectedManagerName = computed(() => selectedManager.value?.name || 'Поточний користувач')

const managerInitials = computed(() => {
  const words = selectedManagerName.value.split(/\s+/).filter(Boolean)
  return words.slice(0, 2).map(word => word[0]).join('').toUpperCase() || 'М'
})
</script>

<style scoped>
.manager-field {
  gap: 7px;
}

.manager-select {
  width: 100%;
}

.manager-select :deep(.el-select__wrapper) {
  min-height: 38px;
  border-radius: 12px;
  box-shadow: 0 0 0 1px #DCE6F2 inset;
}

.manager-readonly {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 42px;
  padding: 7px 9px;
  border: 1px solid #DCE6F2;
  border-radius: 12px;
  background: linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%);
}

.manager-avatar {
  flex: none;
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border-radius: 10px;
  background: linear-gradient(135deg, #1463FF 0%, #0047D1 100%);
  color: #FFFFFF;
  font-size: 11px;
  font-weight: 850;
}

.manager-info {
  min-width: 0;
  display: grid;
  gap: 1px;
}

.manager-info b {
  min-width: 0;
  color: #0F172A;
  font-size: 13px;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.manager-info small {
  color: #64748B;
  font-size: 11px;
}
</style>
