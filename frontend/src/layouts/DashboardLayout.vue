<template>
  <el-container class="dashboard-container">
    <!-- Sidebar -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="logo">
        <div class="logo-icon"><el-icon><Monitor /></el-icon></div>
        <h2 v-if="!isCollapse">NEXORA <span>ERP</span></h2>
      </div>

      <el-scrollbar class="sidebar-scrollbar">
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :router="true"
          class="custom-sidebar-menu"
        >
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <template #title>Головна</template>
          </el-menu-item>

          <el-sub-menu index="inventory" v-if="userStore.hasPermission('inventory.view')">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>Склад</span>
            </template>
            <el-menu-item index="/inventory/nomenclature" v-if="userStore.hasPermission('inventory.nomenclature.view')">Номенклатура</el-menu-item>
            <el-menu-item index="/inventory/warehouses" v-if="userStore.hasPermission('inventory.warehouses.view')">Склади</el-menu-item>
            <el-menu-item index="/inventory/stock" v-if="userStore.hasPermission('inventory.stock.view')">Залишки</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="crm">
            <template #title>
              <el-icon><Tickets /></el-icon>
              <span>CRM</span>
            </template>
            <el-menu-item index="/crm">Замовлення</el-menu-item>
            <el-menu-item index="/crm/analytics">Аналітика</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="sales" v-if="userStore.hasPermission('sales.view')">
            <template #title>
              <el-icon><ShoppingCart /></el-icon>
              <span>Продажі</span>
            </template>
            <el-menu-item index="/sales/counterparties" v-if="userStore.hasPermission('sales.counterparties.view')">Контрагенти</el-menu-item>
            <el-menu-item index="/sales/orders" v-if="userStore.hasPermission('sales.orders.view')">Замовлення</el-menu-item>
            <el-menu-item index="/sales/invoices" v-if="userStore.hasPermission('sales.invoices.view')">Рахунки</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="purchases" v-if="userStore.hasPermission('purchases.view')">
            <template #title>
              <el-icon><Briefcase /></el-icon>
              <span>Закупівлі</span>
            </template>
            <el-menu-item index="/purchases/orders" v-if="userStore.hasPermission('purchases.orders.view')">Замовлення постачальникам</el-menu-item>
            <el-menu-item index="/purchases/planning">Планування</el-menu-item>
            <el-menu-item index="/purchases/receipts" v-if="userStore.hasPermission('purchases.receipts.view')">Прибуткові накладні</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="production">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>Виробництво</span>
            </template>
            <el-menu-item index="/production/orders">Завдання</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="finance" v-if="userStore.hasPermission('finance.view')">
            <template #title>
              <el-icon><Wallet /></el-icon>
              <span>Фінанси</span>
            </template>
            <el-menu-item index="/finance/cash" v-if="userStore.hasPermission('finance.cash.view')">Каса</el-menu-item>
            <el-menu-item index="/finance/bank" v-if="userStore.hasPermission('finance.bank.view')">Банк</el-menu-item>
            <el-menu-item index="/finance/payments" v-if="userStore.hasPermission('finance.payments.view')">Платежі</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="personnel">
            <template #title>
              <el-icon><User /></el-icon>
              <span>Персонал</span>
            </template>
            <el-menu-item index="/personnel/employees">Співробітники</el-menu-item>
            <el-menu-item index="/personnel/departments">Підрозділи</el-menu-item>
            <el-menu-item index="/personnel/payroll">Нарахування ЗП</el-menu-item>
            <el-menu-item index="/personnel/attendance">Табель</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/reports" v-if="userStore.hasPermission('reports.view')">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>Звіти та аналітика</template>
          </el-menu-item>

          <el-sub-menu index="admin" v-if="hasAdministrationAccess">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>Адміністрування</span>
            </template>
            <el-menu-item index="/settings/company" v-if="userStore.hasPermission('settings.manage')">Організація</el-menu-item>
            <el-menu-item index="/settings/dictionaries" v-if="userStore.hasPermission('dictionaries.view')">Довідники</el-menu-item>
            <el-menu-item index="/settings/print-templates" v-if="userStore.hasPermission('print_templates.view')">Шаблони</el-menu-item>
            <el-menu-item index="/settings/trash-bin" v-if="userStore.hasPermission('settings.view')">Корзина</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-scrollbar>

      <div class="sidebar-bottom">
        <el-menu class="bottom-menu">
          <el-menu-item index="quick-actions">
            <el-icon color="#1463FF"><Lightning /></el-icon>
            <template #title><span style="color: #1463FF; font-weight: 600;">Швидкі дії</span></template>
          </el-menu-item>
        </el-menu>
        <div class="sidebar-footer">
          <el-button link @click="toggleTheme()">
            <el-icon><component :is="isDark ? 'Sunny' : 'Moon'" /></el-icon>
          </el-button>
          <el-button link @click="toggleSidebar" v-if="!isCollapse">
            <el-icon><Fold /></el-icon> Згорнути
          </el-button>
        </div>
      </div>
    </el-aside>

    <el-container>
      <!-- Top Header -->
      <el-header class="top-header">
        <div class="header-left">
          <el-button link class="home-btn" @click="router.push('/dashboard')"><el-icon><HomeFilled /></el-icon></el-button>
          <TabsBar class="header-tabs" />
        </div>

        <div class="header-right">
          <el-tooltip content="Пошук по системі" placement="bottom">
            <button class="topbar-icon-btn" type="button" @click="openGlobalSearch">
              <el-icon><Search /></el-icon>
            </button>
          </el-tooltip>

          <!-- Notifications Popover -->
          <el-popover
            placement="bottom-end"
            :width="350"
            trigger="click"
            popper-class="notification-popover"
          >
            <template #reference>
              <el-badge :value="notificationStore.unreadCount" :hidden="notificationStore.unreadCount === 0" class="header-badge">
                <el-button circle link><el-icon><Bell /></el-icon></el-button>
              </el-badge>
            </template>
            
            <div class="notification-panel">
              <div class="notification-header">
                <h3>🔔 Сповіщення</h3>
                <el-link type="primary" :underline="false" @click="notificationStore.readAll()">Прочитати все</el-link>
              </div>
              <el-scrollbar max-height="400px">
                <div v-if="notificationStore.notifications.length === 0" class="empty-notifications">Немає нових сповіщень</div>
                <div v-for="(group, dateName) in groupedNotifications" :key="dateName" class="notification-group">
                  <div class="group-header">{{ dateName }}</div>
                  <div v-for="n in group" :key="n.id" class="notification-item" @click="handleNotificationAction(n)">
                    <div class="ni-dot" :class="'priority-' + getPriorityClass(n.type)"></div>
                    <div class="ni-content">
                      <div class="ni-title">{{ n.title }}</div>
                      <div class="ni-message">{{ n.message }}</div>
                    </div>
                  </div>
                </div>
              </el-scrollbar>
            </div>
          </el-popover>

          <el-button circle link><el-icon><ChatDotRound /></el-icon></el-button>
          
          <el-dropdown @command="handleCommand">
            <div class="user-profile">
              <div class="user-meta">
                <div class="user-name">{{ userStore.user?.firstName }} {{ userStore.user?.lastName }}</div>
                <div class="user-role">Директор</div>
              </div>
              <el-avatar :size="36" src="https://i.pravatar.cc/150?u=a042581f4e29026704d" />
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile"><el-icon><User /></el-icon> Профіль</el-dropdown-item>
                <el-dropdown-item command="users" v-if="userStore.hasPermission('users.view')"><el-icon><UserFilled /></el-icon> Користувачі</el-dropdown-item>
                <el-dropdown-item command="settings"><el-icon><Setting /></el-icon> Налаштування</el-dropdown-item>
                <el-dropdown-item divided command="logout"><el-icon><SwitchButton /></el-icon> Вийти</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Main Content Area -->
      <el-main class="main-content">
        <!-- GLOBAL TAX WARNING -->
        <div v-if="taxWarningVisible" class="tax-limit-warning-banner">
            <el-icon class="mr-2"><WarningFilled /></el-icon>
            Увага! Дохід ФОП наближається до ліміту: <strong>{{ incomePercentage }}%</strong>.
        </div>

        <div class="view-container">
          <router-view v-slot="{ Component }">
            <keep-alive>
              <component :is="Component" :key="route.path" />
            </keep-alive>
          </router-view>
        </div>
      </el-main>
    </el-container>

    <CallResultDialog 
      v-model="callDialogVisible" 
      :task="currentCallTask" 
      @success="notificationStore.fetchNotifications()" 
    />

    <el-dialog
      v-model="globalSearchOpen"
      width="720px"
      class="command-palette-dialog"
      :show-close="false"
      align-center
      @closed="resetGlobalSearch"
    >
      <div class="command-palette">
        <div class="command-search-row">
          <el-icon><Search /></el-icon>
          <input
            ref="searchPaletteInput"
            v-model="globalSearchQuery"
            placeholder="Пошук по системі..."
            @keydown.down.prevent="moveSearchSelection(1)"
            @keydown.up.prevent="moveSearchSelection(-1)"
            @keydown.enter.prevent="openSearchResult(activeSearchResult)"
            @keydown.esc.prevent="globalSearchOpen = false"
          />
          <kbd>Esc</kbd>
        </div>

        <div v-if="!globalSearchQuery.trim()" class="quick-search-sections">
          <button
            v-for="section in quickSearchSections"
            :key="section.path"
            type="button"
            @click="openSearchResult(section)"
          >
            <span class="result-icon">{{ section.icon }}</span>
            <span>{{ section.title }}</span>
          </button>
        </div>

        <div v-else class="search-results-list">
          <div v-if="filteredSearchResults.length === 0" class="search-empty">
            Нічого не знайдено
          </div>
          <button
            v-for="(result, index) in filteredSearchResults"
            :key="`${result.type}-${result.title}-${index}`"
            type="button"
            class="search-result-item"
            :class="{ active: index === activeSearchIndex }"
            @mouseenter="activeSearchIndex = index"
            @click="openSearchResult(result)"
          >
            <span class="result-icon">{{ result.icon }}</span>
            <span class="result-main">
              <strong>{{ result.title }}</strong>
              <small>{{ result.group }}</small>
            </span>
            <span class="result-shortcut">Enter</span>
          </button>
        </div>
      </div>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useDark, useToggle } from '@vueuse/core'
import api from '@/api'
import TabsBar from '@/components/layout/TabsBar.vue'
import CallResultDialog from '@/components/crm/CallResultDialog.vue'
import { useNotificationStore } from '@/stores/notification'

import {
  HomeFilled, Box, ShoppingCart, Briefcase, Wallet, DataAnalysis, Setting,
  Fold, Expand, Bell, User, UserFilled, SwitchButton, Tools, Tickets,
  Monitor, Search, QuestionFilled, ChatDotRound, Lightning, Sunny, Moon, Cpu,
  WarningFilled
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()

const isCollapse = ref(false)
const sidebarWidth = computed(() => isCollapse.value ? '64px' : '260px')
const activeMenu = computed(() => route.path)
const globalSearchOpen = ref(false)
const globalSearchQuery = ref('')
const activeSearchIndex = ref(0)
const searchPaletteInput = ref(null)

const isDark = useDark()
const toggleTheme = useToggle(isDark)

const hasAdministrationAccess = computed(() => [
  'settings.view', 'settings.manage', 'dictionaries.view', 'print_templates.view', 'business_processes.view', 'users.view'
].some(p => userStore.hasPermission(p)))

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const quickSearchSections = [
  { title: 'Номенклатура', group: 'Розділ', icon: 'NM', path: '/inventory/nomenclature' },
  { title: 'Замовлення', group: 'Продажі', icon: 'SO', path: '/sales/orders' },
  { title: 'CRM', group: 'CRM', icon: 'CRM', path: '/crm' },
  { title: 'Закупівлі', group: 'Закупівлі', icon: 'PO', path: '/purchases/orders' },
  { title: 'Прибуткові накладні', group: 'Закупівлі', icon: 'PR', path: '/purchases/receipts' },
  { title: 'Клієнти', group: 'Продажі', icon: 'CL', path: '/sales/counterparties' },
  { title: 'Постачальники', group: 'Закупівлі', icon: 'SU', path: '/sales/counterparties' },
]

const searchResults = [
  { title: 'Профіль 30x30*1,2', group: 'Номенклатура', icon: 'NM', path: '/inventory/nomenclature' },
  { title: 'ДСП Sonoma 18 мм', group: 'Номенклатура', icon: 'NM', path: '/inventory/nomenclature' },
  { title: 'PO-00006', group: 'Документи', icon: 'PO', path: '/purchases/orders' },
  { title: 'PR-00004', group: 'Документи', icon: 'PR', path: '/purchases/receipts' },
  { title: 'Заявка Jack', group: 'CRM', icon: 'CRM', path: '/crm' },
  { title: 'Замовлення постачальникам', group: 'Закупівлі', icon: 'PO', path: '/purchases/orders' },
  { title: 'Контрагенти', group: 'Клієнти і постачальники', icon: 'CP', path: '/sales/counterparties' },
]

const filteredSearchResults = computed(() => {
  const query = globalSearchQuery.value.trim().toLowerCase()
  if (!query) return []
  return searchResults.filter(item =>
    item.title.toLowerCase().includes(query) ||
    item.group.toLowerCase().includes(query)
  )
})

const activeSearchResult = computed(() => filteredSearchResults.value[activeSearchIndex.value])

const openGlobalSearch = () => {
  globalSearchOpen.value = true
  nextTick(() => searchPaletteInput.value?.focus())
}

const resetGlobalSearch = () => {
  globalSearchQuery.value = ''
  activeSearchIndex.value = 0
}

const moveSearchSelection = (direction) => {
  const count = filteredSearchResults.value.length
  if (!count) return
  activeSearchIndex.value = (activeSearchIndex.value + direction + count) % count
}

const openSearchResult = (result) => {
  if (!result?.path) return
  globalSearchOpen.value = false
  router.push(result.path)
}

const handleGlobalSearchKeydown = (event) => {
  const isMac = navigator.platform.toLowerCase().includes('mac')
  const modifierPressed = isMac ? event.metaKey : event.ctrlKey
  if (modifierPressed && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    openGlobalSearch()
  }
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile': router.push('/profile'); break
    case 'users': router.push('/settings/users'); break
    case 'settings': router.push('/settings'); break
    case 'logout':
      notificationStore.stopPolling()
      userStore.logout()
      ElMessage.success('Ви вийшли з системи')
      router.push('/login')
      break
  }
}

// Notifications Logic
const callDialogVisible = ref(false)
const currentCallTask = ref(null)

const groupedNotifications = computed(() => {
  const groups = {}
  notificationStore.notifications.forEach(n => {
    const d = new Date(n.created_at).toLocaleDateString()
    if (!groups[d]) groups[d] = []
    groups[d].push(n)
  })
  return groups
})

const getPriorityClass = (type) => {
  if (['CALL', 'DEADLINE_OVERDUE'].includes(type)) return 'red'
  if (['DEADLINE_SOON', 'STALE_LEAD'].includes(type)) return 'yellow'
  return 'blue'
}

const handleNotificationAction = (n) => {
  if (n.type === 'CALL') {
    currentCallTask.value = { id: n.data.task_id, order_id: n.data.real_order_id, client_phone: n.data.client_phone }
    callDialogVisible.value = true
  } else if (n.data?.order_id) {
    router.push({ name: 'crm-order-edit', params: { id: n.data.order_id } })
  }
}

// Tax Warning
const taxWarningVisible = ref(false)
const incomePercentage = ref(0)

onMounted(async () => {
    window.addEventListener('keydown', handleGlobalSearchKeydown)
    notificationStore.startPolling()
    try {
        const res = await api.get('/api/v1/finance/fop-income')
        if (res.data && res.data.percentage >= 95) {
            incomePercentage.value = res.data.percentage
            taxWarningVisible.value = true
        }
    } catch (e) {}
})

onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleGlobalSearchKeydown)
    notificationStore.stopPolling()
})

watch(globalSearchQuery, () => {
  activeSearchIndex.value = 0
})
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  background-color: var(--erp-bg-page);
}

.sidebar {
  background: var(--erp-sidebar-bg);
  border-right: 1px solid var(--erp-sidebar-border);
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 12px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: var(--erp-primary);
  border-radius: 8px;
  display: grid;
  place-items: center;
  color: #FFF;
  font-size: 18px;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: #1E293B;
  letter-spacing: 0.5px;
}

.logo h2 span { color: var(--erp-primary); }

.custom-sidebar-menu { border: none; background: transparent; }

.custom-sidebar-menu :deep(.el-menu-item),
.custom-sidebar-menu :deep(.el-sub-menu__title) {
  color: var(--erp-sidebar-text) !important;
  margin: 4px 12px;
  border-radius: 10px;
  height: 44px;
  line-height: 44px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.custom-sidebar-menu :deep(.el-icon) {
  font-size: 20px;
  margin-right: 8px;
  transition: transform 0.2s ease;
}

.custom-sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: var(--erp-sidebar-active-bg) !important;
  color: var(--erp-primary) !important;
  font-weight: 600;
}

.custom-sidebar-menu :deep(.el-menu-item.is-active .el-icon) {
  transform: scale(1.1);
}

.custom-sidebar-menu :deep(.el-menu-item:hover),
.custom-sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: var(--erp-bg-surface-soft) !important;
  color: var(--erp-primary) !important;
}

.sidebar-bottom { border-top: 1px solid var(--erp-sidebar-border); padding: 12px 0; }
.sidebar-footer { padding: 8px 24px; display: flex; align-items: center; gap: 12px; color: var(--erp-text-muted); font-size: 14px; }

.top-header {
  background: #FFFFFF;
  border-bottom: 1px solid var(--erp-sidebar-border);
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  padding: 0 24px;
  height: 64px;
  gap: 14px;
}

.header-left { display: flex; align-items: center; gap: 14px; overflow: hidden; min-width: 0; }
.header-tabs { flex: 1; min-width: 0; }

.header-right { display: flex; align-items: center; justify-content: flex-end; gap: 8px; flex-shrink: 0; }

.topbar-icon-btn {
  width: 38px;
  height: 38px;
  border: 1px solid #E6ECF3;
  border-radius: 12px;
  background: #FFFFFF;
  color: #475569;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background .18s, border-color .18s, color .18s;
}

.topbar-icon-btn:hover {
  background: #F5F8FC;
  border-color: #D8E1ED;
  color: #1463FF;
}

.command-palette-dialog :deep(.el-dialog) {
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(16, 24, 40, 0.14);
}

.command-palette-dialog :deep(.el-dialog__header) {
  display: none;
}

.command-palette-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.command-palette {
  background: #FFFFFF;
  border: 1px solid #E6ECF3;
  border-radius: 18px;
  overflow: hidden;
}

.command-search-row {
  height: 64px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-bottom: 1px solid #E6ECF3;
}

.command-search-row .el-icon {
  color: #64748B;
  font-size: 20px;
}

.command-search-row input {
  flex: 1;
  height: 48px;
  border: 0;
  outline: none;
  color: #0F172A;
  font-size: 16px;
  font-weight: 600;
}

.command-search-row input::placeholder {
  color: #94A3B8;
  font-weight: 500;
}

.command-search-row kbd,
.result-shortcut {
  border: 1px solid #D8E1ED;
  border-radius: 7px;
  padding: 3px 7px;
  background: #F8FAFC;
  color: #64748B;
  font-size: 11px;
  font-weight: 700;
}

.quick-search-sections {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  padding: 14px;
}

.quick-search-sections button,
.search-result-item {
  min-height: 48px;
  border: 0;
  border-radius: 12px;
  background: #FFFFFF;
  color: #1E293B;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  text-align: left;
  cursor: pointer;
}

.quick-search-sections button:hover,
.search-result-item:hover,
.search-result-item.active {
  background: #F5F8FC;
}

.result-icon {
  min-width: 34px;
  height: 34px;
  border-radius: 10px;
  background: #EEF2FF;
  color: #3730A3;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 900;
}

.search-results-list {
  padding: 10px;
  max-height: 430px;
  overflow-y: auto;
}

.search-result-item {
  width: 100%;
  justify-content: flex-start;
}

.result-main {
  flex: 1;
  min-width: 0;
}

.result-main strong,
.result-main small {
  display: block;
}

.result-main strong {
  color: #0F172A;
  font-size: 14px;
}

.result-main small {
  margin-top: 2px;
  color: #64748B;
  font-size: 12px;
}

.search-empty {
  padding: 34px 16px;
  color: #64748B;
  text-align: center;
  font-size: 14px;
}

.header-badge :deep(.el-badge__content) {
  top: 10px !important;
  right: 10px !important;
  transform: scale(0.8) translate(50%, -50%);
  border: 2px solid #FFF;
}

.user-profile { display: flex; align-items: center; gap: 12px; cursor: pointer; padding: 4px 8px; border-radius: 12px; transition: background 0.2s; }
.user-profile:hover { background: var(--erp-bg-surface-soft); }
.user-meta { text-align: right; }
.user-name { font-size: 13px; font-weight: 700; color: var(--erp-text-heading); line-height: 1.2; }
.user-role { font-size: 11px; color: var(--erp-text-muted); }

.tax-limit-warning-banner { background: #FDECEE; color: #EF4444; padding: 8px 24px; font-size: 13px; display: flex; align-items: center; }

.notification-panel { padding: 12px; }
.notification-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.notification-item { padding: 8px; border-radius: 8px; cursor: pointer; display: flex; gap: 10px; align-items: flex-start; }
.notification-item:hover { background: #F8FAFC; }
.ni-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; }
.priority-red { background: #EF4444; }
.priority-yellow { background: #F59E0B; }
.priority-blue { background: #3B82F6; }
.ni-title { font-weight: 700; font-size: 13px; }
.ni-message { font-size: 12px; color: var(--erp-text-muted); }

.main-content { padding: 0; }
.view-container {
  padding: 24px;
  position: relative;
  min-height: 100%;
}
</style>
