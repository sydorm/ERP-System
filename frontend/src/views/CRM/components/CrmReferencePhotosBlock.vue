<template>
  <div class="crm-field">
    <label class="crm-label">Фото референс від клієнта</label>
    <div class="photo-upload-zone" @click="photoInput?.click()">
      <img v-if="form.reference_photo" :src="form.reference_photo" class="photo-preview" />
      <div v-else class="photo-placeholder">
        <el-icon><Picture /></el-icon>
        <span>+ Завантажити фото</span>
      </div>
    </div>
    <input ref="photoInput" type="file" accept="image/*" style="display:none" @change="$emit('upload-photo', $event)" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Picture } from '@element-plus/icons-vue'

defineProps({
  form: { type: Object, required: true },
})

defineEmits(['upload-photo'])
const photoInput = ref(null)
</script>
