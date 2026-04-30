<template>
  <div class="crm-section">
    <div class="crm-section-title" style="margin-bottom:8px">Історія</div>
    <div class="history-list">
      <div class="history-item" v-for="(h, i) in history" :key="i">
        <span class="h-dot" />
        <div class="h-body">
          <span class="h-text">{{ h.text }}</span>
          <span class="h-time">{{ h.time }}</span>
        </div>
      </div>
    </div>

    <div class="crm-field" style="margin-top:10px">
      <label class="crm-label">Додати нотатку</label>
      <el-input
        v-model="form.internal_notes"
        type="textarea"
        :rows="3"
        placeholder="Запис менеджера..."
      />
    </div>
  </div>
</template>

<script setup>
defineProps({
  form: { type: Object, required: true },
  history: { type: Array, required: true },
})
</script>
