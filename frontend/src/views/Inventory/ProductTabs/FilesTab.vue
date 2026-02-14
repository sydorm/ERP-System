<template>
  <el-card shadow="never" class="tab-card">
    <el-upload
      class="upload-demo"
      drag
      action="#"
      multiple
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        Перетягніть файли сюди або <em>натисніть для завантаження</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          Креслення, сертифікати, PDF-інструкції (до 10MB)
        </div>
      </template>
    </el-upload>
  </el-card>
</template>

<script setup>
import { UploadFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
.tab-card {
  margin: 24px;
  border: 1px solid #eef0f2;
}
</style>
