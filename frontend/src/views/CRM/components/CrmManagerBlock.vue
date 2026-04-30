<template>
  <div class="crm-field manager-field">
    <label class="crm-label">Відповідальний менеджер</label>
    <el-select
      v-model="form.manager_id"
      filterable
      placeholder="Оберіть менеджера"
      style="width:100%"
      :disabled="!canReassignManager"
    >
      <el-option
        v-for="u in managerOptions"
        :key="u.id"
        :label="u.name"
        :value="u.id"
      />
    </el-select>
    <small v-if="!canReassignManager" class="field-help">
      Призначається автоматично. Змінювати може директор або користувач із правом crm.order.reassign.
    </small>
  </div>
</template>

<script setup>
defineProps({
  form: { type: Object, required: true },
  managerOptions: { type: Array, required: true },
  canReassignManager: { type: Boolean, default: false },
})
</script>
