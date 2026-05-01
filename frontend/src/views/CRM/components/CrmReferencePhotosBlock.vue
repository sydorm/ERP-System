<template>
  <div class="reference-photos-container-premium">
    <div
      class="upload-zone-wrapper"
      :class="{ 'has-photo': displayPhoto, 'is-dragging': isDragging }"
      @click="photoInput?.click()"
      @dragenter.prevent="isDragging = true"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <div v-if="displayPhoto" class="preview-overlay">
        <img :src="displayPhoto" class="photo-preview-image" />
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
          <span class="sub-text">JPG, PNG або WEBP. Перетягніть файл сюди</span>
        </div>
        <div class="upload-hint-row">
          <span>Drag & drop</span>
          <span>Preview одразу</span>
        </div>
      </div>
    </div>
    <input
      ref="photoInput"
      type="file"
      accept="image/*"
      style="display:none"
      @change="handleFileInput"
    />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { Picture, Refresh } from '@element-plus/icons-vue'

const props = defineProps({
  form: { type: Object, required: true },
})

const emit = defineEmits(['upload-photo'])
const photoInput = ref(null)
const localPreview = ref('')
const isDragging = ref(false)

const displayPhoto = computed(() => (
  localPreview.value
  || props.form.reference_photo
  || props.form.photos?.find(photo => typeof photo === 'string')
  || props.form.photos?.find(photo => photo?.preview_url)?.preview_url
  || ''
))

const setPreview = (file) => {
  if (!file) return
  if (localPreview.value && localPreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(localPreview.value)
  }
  localPreview.value = URL.createObjectURL(file)
  emit('upload-photo', {
    name: file.name,
    size: file.size,
    type: file.type,
    preview_url: localPreview.value,
  })
}

const handleFileInput = (event) => {
  setPreview(event.target.files?.[0])
  event.target.value = ''
}

const handleDrop = (event) => {
  isDragging.value = false
  setPreview(event.dataTransfer?.files?.[0])
}

onBeforeUnmount(() => {
  if (localPreview.value && localPreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(localPreview.value)
  }
})
</script>

<style scoped>
.reference-photos-container-premium {
  width: 100%;
}

.upload-zone-wrapper {
  position: relative;
  width: 100%;
  min-height: 172px;
  background:
    radial-gradient(circle at 50% 0%, rgba(21, 185, 122, .08), transparent 34%),
    #fff;
  border: 1.5px dashed #E2E8F0;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.upload-zone-wrapper:hover {
  border-color: #10B981;
  background: #F0FDF4;
  border-style: solid;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02), 0 12px 28px rgba(21,185,122,.10);
  transform: translateY(-1px);
}

.upload-zone-wrapper.is-dragging {
  border-color: #15B97A;
  background: #ECFDF5;
  box-shadow: 0 0 0 4px rgba(21,185,122,.08), 0 16px 30px rgba(21,185,122,.14);
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
  width: 54px;
  height: 54px;
  background:
    linear-gradient(180deg, #FFFFFF, #F8FAFC);
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-size: 26px;
  color: #10B981;
  border: 1px solid #DDF7EA;
  box-shadow: 0 12px 22px rgba(15, 23, 42, 0.08);
  transition: all 0.3s ease;
}

.upload-zone-wrapper:hover .icon-circle {
  transform: scale(1.1) rotate(5deg);
  background: #10B981;
  color: white;
}

.text-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.main-text {
  font-size: 15px;
  font-weight: 800;
  color: #1E293B;
}

.sub-text {
  font-size: 11px;
  color: #94A3B8;
  font-weight: 600;
}

.upload-hint-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.upload-hint-row span {
  padding: 4px 8px;
  border: 1px solid #DDF7EA;
  border-radius: 999px;
  color: #047857;
  background: #ECFDF5;
  font-size: 10px;
  font-weight: 850;
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

.upload-zone-wrapper:hover .photo-preview-image {
  filter: saturate(1.05) contrast(.96);
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
