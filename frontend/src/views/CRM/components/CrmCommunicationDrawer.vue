<template>
  <el-drawer
    v-model="visibleModel"
    title="Швидкий контакт / Комунікація"
    direction="rtl"
    size="380px"
  >
    <div style="display: flex; flex-direction: column; gap: 16px;">
      <div style="font-size: 13px; font-weight: 600; color: #374151;">Оберіть канал зв'язку:</div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <button
          v-for="ct in communicationTypes"
          :key="ct.code"
          style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; padding: 14px; border: 1.5px solid #E5E7EB; border-radius: 12px; background: white; cursor: pointer; transition: all 0.2s;"
          :style="{
            borderColor: contactCommType === ct.code ? '#3D3AA8' : '#E5E7EB',
            background: contactCommType === ct.code ? '#F5F5FF' : 'white',
          }"
          @click="selectChannel(ct)"
        >
          <span style="font-size: 24px;">{{ ct.icon }}</span>
          <span style="font-size: 13px; font-weight: 600; color: #1F2937;">{{ ct.name }}</span>
        </button>
      </div>

      <div style="margin-top: 12px; border-top: 1px solid #E5E7EB; padding-top: 16px;">
        <div style="font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 10px;">Швидкі шаблони повідомлень:</div>
        <div style="display: flex; flex-direction: column; gap: 8px;">
          <div
            v-for="(tpl, idx) in messageTemplates"
            :key="idx"
            style="padding: 10px; border: 1px solid #E5E7EB; border-radius: 8px; cursor: pointer; transition: background 0.2s;"
            @click="applyTemplate(tpl)"
            onmouseover="this.style.background='#F9FAFB'"
            onmouseout="this.style.background='white'"
          >
            <div style="font-size: 12px; font-weight: 700; color: #1F2937; margin-bottom: 4px;">{{ tpl.title }}</div>
            <div style="font-size: 11px; color: #6B7280; line-height: 1.3;">{{ tpl.text }}</div>
          </div>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  communicationTypes: { type: Array, required: true },
  contactCommType: { type: String, default: 'CALL' },
  messageTemplates: { type: Array, required: true },
})

const emit = defineEmits(['update:modelValue', 'update:contactCommType', 'apply-template'])

const visibleModel = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value),
})

const selectChannel = (ct) => {
  emit('update:contactCommType', ct.code)
  ElMessage.success(`Обрано канал: ${ct.name}`)
}

const applyTemplate = (tpl) => {
  emit('apply-template', tpl.text)
  ElMessage.success('Шаблон застосовано!')
}
</script>
