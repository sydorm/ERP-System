<template>
  <el-card shadow="never" class="tab-card">
    <h3>Поточні залишки</h3>
    <el-table :data="stockLevels" border style="width: 100%; margin-top: 15px">
      <el-table-column prop="warehouse" label="Склад" />
      <el-table-column prop="quantity" label="Наявність" width="150" align="center" />
      <el-table-column prop="reserved" label="Резерв" width="150" align="center" />
      <el-table-column prop="available" label="Доступно" width="150" align="center" />
      <el-table-column prop="minLevel" label="Мін. очікування" width="150" align="center">
        <template #default="scope">
          <el-input-number v-model="scope.row.minLevel" size="small" />
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
const props = defineProps({
  stockLevels: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.tab-card {
  margin: 24px;
  border: 1px solid #eef0f2;
}
</style>
