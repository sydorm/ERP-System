<template>
  <div class="autogrid-container">
    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-if="config.searchable"
          v-model="searchQuery"
          :placeholder="config.searchPlaceholder || 'Пошук...'"
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
        />
        <slot name="toolbar-left"></slot>
      </div>
      <div class="toolbar-right">
        <slot name="toolbar-right"></slot>
        <el-button
          v-if="config.creatable"
          type="primary"
          :icon="Plus"
          @click="$emit('create')"
        >
          {{ config.createLabel || 'Додати' }}
        </el-button>
        <el-button :icon="Refresh" circle @click="fetchData" />
      </div>
    </div>

    <!-- Table -->
    <el-table
      v-loading="loading"
      :data="data"
      stripe
      border
      style="width: 100%"
      @row-click="(row) => $emit('row-click', row)"
    >
      <el-table-column
        v-for="col in config.columns"
        :key="col.prop"
        :prop="col.prop"
        :label="col.label"
        :width="col.width"
        :align="col.align || 'left'"
        :sortable="col.sortable"
      >
        <template #default="scope">
          <!-- Custom cell slot -->
          <slot :name="'col-' + col.prop" :row="scope.row" :value="scope.row[col.prop]">
            <!-- Default rendering based on type -->
            <template v-if="col.type === 'currency'">
              {{ formatCurrency(scope.row[col.prop], scope.row[col.currencyProp || 'currency']) }}
            </template>
            <template v-else-if="col.type === 'date'">
              {{ formatDate(scope.row[col.prop]) }}
            </template>
            <template v-else-if="col.type === 'status'">
              <el-tag :type="getStatusType(scope.row[col.prop])">
                {{ scope.row[col.prop] }}
              </el-tag>
            </template>
            <template v-else>
              {{ scope.row[col.prop] }}
            </template>
          </slot>
        </template>
      </el-table-column>

      <!-- Actions Column -->
      <el-table-column v-if="config.showActions" label="Дії" width="120" fixed="right" align="center">
        <template #default="scope">
          <el-button-group>
            <el-button
              size="small"
              :icon="Edit"
              @click.stop="$emit('edit', scope.row)"
            />
            <el-button
              size="small"
              type="danger"
              :icon="Delete"
              @click.stop="$emit('delete', scope.row)"
            />
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        :total="total"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Search, Plus, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  config: {
    type: Object,
    required: true
    /**
     * Config structure:
     * {
     *   endpoint: string,
     *   searchable: boolean,
     *   creatable: boolean,
     *   columns: Array<{ prop, label, type, width, align, sortable }>,
     *   showActions: boolean
     * }
     */
  },
  filters: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['create', 'edit', 'delete', 'row-click'])

// State
const data = ref([])
const total = ref(0)
const loading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchQuery.value || undefined,
      ...props.filters
    }
    const res = await api.get(props.config.endpoint, { params })
    data.value = res.data
    // Mock total for now, or use response total if available
    total.value = data.value.length < pageSize.value ? data.value.length + (currentPage.value - 1) * pageSize.value : 100
  } catch (error) {
    console.error('Fetch error:', error)
  } finally {
    loading.value = false
  }
}

let searchTimeout = null
const handleSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchData()
  }, 500)
}

const formatCurrency = (val, curr) => {
  return new Intl.NumberFormat('uk-UA', { style: 'currency', currency: curr || 'UAH' }).format(val)
}

const formatDate = (val) => {
  if (!val) return '-'
  return new Date(val).toLocaleDateString('uk-UA')
}

const getStatusType = (status) => {
  const map = {
    'new': 'info',
    'processing': 'warning',
    'shipped': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return map[status?.toLowerCase()] || 'info'
}

watch(() => props.filters, () => {
  currentPage.value = 1
  fetchData()
}, { deep: true })

onMounted(fetchData)

defineExpose({ fetchData })
</script>

<style scoped>
.autogrid-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  width: 300px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
