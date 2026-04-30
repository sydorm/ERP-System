<template>
  <el-dialog v-model="visibleModel" title="Новий клієнт" width="460px" class="saas-dialog">
    <div class="crm-grid-2">
      <div class="crm-field">
        <label class="crm-label">Ім'я та прізвище *</label>
        <el-input v-model="newClient.name" placeholder="Введіть повне ім'я" />
      </div>
      <div class="crm-field">
        <label class="crm-label">Телефон</label>
        <el-input v-model="newClient.phone" placeholder="+380..." />
      </div>
    </div>
    <div class="crm-field">
      <label class="crm-label">Email</label>
      <el-input v-model="newClient.email" placeholder="example@mail.com" />
    </div>
    <template #footer>
      <el-button @click="visibleModel = false" style="border-radius: 8px;">Скасувати</el-button>
      <el-button class="saas-btn-primary" @click="$emit('create')" :loading="saving" style="border-radius: 8px;">Створити клієнта</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  newClient: { type: Object, required: true },
  saving: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'create'])

const visibleModel = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value),
})
</script>
