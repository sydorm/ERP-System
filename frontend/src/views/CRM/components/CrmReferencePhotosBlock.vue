<template>
  <div class="reference-photos-container-premium">
    <div class="upload-zone-wrapper" :class="{ 'has-photo': form.reference_photo }" @click="photoInput?.click()">
      <div v-if="form.reference_photo" class="preview-overlay">
        <img :src="form.reference_photo" class="photo-preview-image" />
        <div class="overlay-actions">
          <div class="action-badge">
            <el-icon><Refresh /></el-icon>
            Змінити фото
          </div>
        </div>
      </div>
      <div v-else class="placeholder-content">
        <div class="icon-circle">
          <el-icon><Picture /></el-icon>
        </div>
        <div class="text-group">
          <span class="main-text">Завантажити референс</span>
          <span class="sub-text">Перетягніть файл або натисніть сюди</span>
        </div>
      </div>
    </div>
    <input
      ref="photoInput"
      type="file"
      accept="image/*"
      style="display:none"
      @change="$emit('upload-photo', $event)"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Picture, Refresh } from '@element-plus/icons-vue'

defineProps({
  form: { type: Object, required: true },
})

defineEmits(['upload-photo'])
const photoInput = ref(null)
</script>

<style scoped>
.reference-photos-container-premium {
  width: 100%;
}

.upload-zone-wrapper {
  position: relative;
  width: 100%;
  min-height: 140px;
  background: #F8FAFC;
  border: 2px dashed #E2E8F0;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.upload-zone-wrapper:hover {
  border-color: #10B981;
  background: #F0FDF4;
  transform: translateY(-2px);
}

.upload-zone-wrapper.has-photo {
  border-style: solid;
  border-color: #F1F5F9;
  background: #fff;
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
  padding: 24px;
}

.icon-circle {
  width: 48px;
  height: 48px;
  background: #fff;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 24px;
  color: #10B981;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.text-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.main-text {
  font-size: 14px;
  font-weight: 800;
  color: #1E293B;
}

.sub-text {
  font-size: 11px;
  color: #64748B;
  font-weight: 600;
}

.preview-overlay {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

.photo-preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: filter 0.3s ease;
}

.overlay-actions {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.4);
  display: grid;
  place-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  backdrop-filter: blur(2px);
}

.upload-zone-wrapper:hover .overlay-actions {
  opacity: 1;
}

.action-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 800;
  color: #0F172A;
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}
</style>
