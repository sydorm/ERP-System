<template>
  <el-card shadow="never" class="tab-card">
    <el-form :model="modelValue" :rules="rules" label-position="top">
      <el-row :gutter="40">
        <el-col :span="16">
          <el-form-item label="Назва товару" prop="name">
            <el-input v-model="modelValue.name" size="large" placeholder="Введіть назву (напр., Нога стола чорна 710мм)" />
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Артикул (SKU)" prop="sku">
                <el-input v-model="modelValue.sku" placeholder="WOOD-001" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Категорія" prop="category">
                <el-select v-model="modelValue.category" placeholder="Оберіть категорію" style="width: 100%">
                  <el-option v-for="opt in categoryOptions" :key="opt.code" :label="opt.name" :value="opt.code" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Опис товару">
            <el-input v-model="modelValue.description" type="textarea" :rows="5" placeholder="Докладний опис товару, технічні характеристики..." />
          </el-form-item>
        </el-col>

        <el-col :span="8">
          <el-form-item label="Зображення">
            <div class="image-upload-zone">
              <el-image v-if="modelValue.image_url" :src="modelValue.image_url" fit="cover" class="preview-image" />
              <div v-else class="upload-placeholder">
                <el-icon :size="40"><Picture /></el-icon>
                <span>Натисніть для завантаження</span>
              </div>
            </div>
          </el-form-item>
          
          <el-form-item label="Одиниця виміру">
            <el-select v-model="modelValue.unit_of_measure" style="width: 100%">
              <el-option v-for="opt in uomOptions" :key="opt.code" :label="opt.name" :value="opt.code" />
            </el-select>
          </el-form-item>

          <el-form-item label="Статус">
            <el-switch v-model="modelValue.is_active" active-text="Активний" inactive-text="Архівний" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
  </el-card>
</template>

<script setup>
import { Picture } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  categoryOptions: {
    type: Array,
    default: () => []
  },
  uomOptions: {
    type: Array,
    default: () => []
  },
  rules: {
    type: Object,
    default: () => ({})
  }
})
</script>

<style scoped>
.tab-card {
    margin: 24px;
    border: 1px solid #eef0f2;
}

.image-upload-zone {
    width: 100%;
    height: 200px;
    border: 2px dashed #dcdfe6;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    background: white;
    transition: all 0.2s;
}

.image-upload-zone:hover {
    border-color: #409eff;
    color: #409eff;
}

.upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    color: #909399;
}

.preview-image {
    width: 100%;
    height: 100%;
    border-radius: 6px;
}
</style>
