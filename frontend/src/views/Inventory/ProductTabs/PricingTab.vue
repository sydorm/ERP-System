<template>
  <el-card shadow="never" class="tab-card">
    <el-row :gutter="40">
      <el-col :span="12">
        <h3>Ціноутворення</h3>
        <el-form label-position="left" label-width="150px" style="margin-top: 20px">
          <el-form-item label="Ціна продажу">
            <el-input-number v-model="modelValue.price" :precision="2" :step="1" style="width: 200px" />
            <el-select v-model="modelValue.currency" style="width: 100px; margin-left: 10px">
              <el-option v-for="c in currencyOptions" :key="c.code" :label="c.code" :value="c.code" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="Собівартість">
            <el-input-number v-model="modelValue.cost" :precision="2" :step="1" style="width: 200px" />
            <span class="cost-hint" v-if="hasSpecification">Рахується автоматично за специфікацією</span>
          </el-form-item>

          <el-form-item label="Націнка (%)">
            <el-tag :type="markupTagType" size="large" effect="dark">
              {{ calculateMarkup }}%
            </el-tag>
          </el-form-item>
        </el-form>
      </el-col>
      
      <el-col :span="12">
        <div class="chart-placeholder">
          <el-empty description="Тут буде графік історії зміни цін" />
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  currencyOptions: {
    type: Array,
    default: () => []
  },
  hasSpecification: {
    type: Boolean,
    default: false
  }
})

const calculateMarkup = computed(() => {
  if (!props.modelValue.price || !props.modelValue.cost) return 0
  return (((props.modelValue.price - props.modelValue.cost) / props.modelValue.cost) * 100).toFixed(1)
})

const markupTagType = computed(() => {
  const markup = parseFloat(calculateMarkup.value)
  if (markup >= 30) return 'success'
  if (markup >= 15) return 'warning'
  return 'danger'
})
</script>

<style scoped>
.tab-card {
  margin: 24px;
  border: 1px solid #eef0f2;
}

.cost-hint {
  margin-left: 12px;
  font-size: 12px;
  color: #909399;
  font-style: italic;
}

.chart-placeholder {
  height: 300px;
  background: #fdfdfd;
  border: 1px dashed #ebeef5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
