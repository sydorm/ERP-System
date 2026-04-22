<template>
  <el-container class="dashboard-container">
    <!-- Sidebar -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="logo">
        <h2 v-if="!isCollapse">ERP System</h2>
        <h2 v-else>ERP</h2>
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

        <el-menu-item index="/crm">
          <el-icon><Tickets /></el-icon>
          <template #title>CRM</template>
        </el-menu-item>

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
          <el-menu-item index="/purchases/orders" v-if="userStore.hasPermission('purchases.orders.view')">Замовлення</el-menu-item>
          <el-menu-item index="/purchases/receipts" v-if="userStore.hasPermission('purchases.receipts.view')">Прибуткові накладні</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="production">
          <template #title>
            <el-icon><Tools /></el-icon>
            <span>Виробництво</span>
          </template>
          <el-menu-item index="/production/orders">Завдання на виробництво</el-menu-item>
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
          <el-menu-item index="/personnel/hr-reports">Звіти по ЗП</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/reports" v-if="userStore.hasPermission('reports.view')">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>Звіти</template>
        </el-menu-item>

        <!-- Previews removed -->
        <!-- Administration Section -->
        <el-sub-menu index="admin" v-if="userStore.hasPermission('settings.view')">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>Адміністрування</span>
          </template>
          <el-menu-item index="/settings/company">Організація</el-menu-item>

          <el-menu-item index="/settings/dictionaries">Довідники</el-menu-item>
          <el-menu-item index="/settings/trash-bin">Корзина</el-menu-item>
        </el-sub-menu>

        <!-- Settings submenu removed as Users moved to profile dropdown -->
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- Main Content -->
    <el-container>
      <!-- Top Header -->
      <el-header class="top-header">
        <div class="header-left">
          <el-button
            :icon="isCollapse ? Expand : Fold"
            @click="toggleSidebar"
            circle
          />
          <h2 class="top-page-title">{{ currentRouteTitle }}</h2>
        </div>

        <div class="header-right">
          <!-- Theme Toggle -->
          <el-button 
            @click="toggleTheme()" 
            circle 
            class="theme-toggle-btn"
          >
            <span v-if="isDark">☀️</span>
            <span v-else>🌙</span>
          </el-button>

          <!-- Notifications Bell -->
          <el-popover
            placement="bottom-end"
            :width="350"
            trigger="click"
            popper-class="notification-popover"
          >
            <template #reference>
              <el-badge :value="notificationStore.unreadCount" :hidden="notificationStore.unreadCount === 0" class="notification-badge">
                <el-button :icon="Bell" circle :class="{ 'bell-ringing': hasOverdueCalls }" />
              </el-badge>
            </template>
            
            <div class="notification-panel">
              <div class="notification-header">
                <h3>🔔 Сповіщення</h3>
                <el-link type="primary" :underline="false" @click="notificationStore.readAll()">Прочитати все</el-link>
              </div>
              
              <el-scrollbar max-height="500px">
                <div v-if="notificationStore.notifications.length === 0" class="empty-notifications">
                  <span class="empty-icon">🔔</span>
                  <p>Немає нових сповіщень</p>
                </div>
                
                <div v-else class="notification-groups">
                  <div v-for="(group, dateName) in groupedNotifications" :key="dateName" class="notification-group">
                    <div class="group-header">{{ dateName }}</div>
                    
                    <div 
                      v-for="n in group" 
                      :key="n.id" 
                      class="notification-item"
                      :class="{ 
                        'is-urgent': n.type === 'CALL' || n.type === 'DEADLINE_OVERDUE',
                        'is-warning': n.type === 'STALE_LEAD' || n.type === 'DEADLINE_SOON'
                      }"
                    >
                      <div class="ni-dot" :class="'priority-' + getPriorityClass(n.type)"></div>
                      
                      <div class="ni-content">
                        <div class="ni-title">
                          <span v-if="n.type === 'CALL'" class="ni-time">{{ formatTime(n.created_at) }} — </span>
                          {{ n.title }}
                        </div>
                        <div class="ni-message">{{ n.message }}</div>
                        <div v-if="n.data && n.data.client_phone" class="ni-phone">
                          {{ n.data.client_phone }}
                        </div>
                      </div>

                      <div class="ni-actions">
                        <el-button 
                          @click="handleNotificationAction(n)"
                          size="small" 
                          circle
                          class="action-btn"
                          :icon="ArrowRight"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </el-scrollbar>
            </div>
          </el-popover>

          <el-dropdown @command="handleCommand">
            <div class="user-avatar">
              <el-avatar :size="40">
                <el-icon><User /></el-icon>
              </el-avatar>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <div class="user-info">
                    <div class="user-name">{{ userStore.user?.firstName }} {{ userStore.user?.lastName }}</div>
                    <div class="user-email">{{ userStore.user?.email }}</div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item divided command="profile">
                  <el-icon><User /></el-icon>
                  Профіль
                </el-dropdown-item>
                <el-dropdown-item v-if="userStore.hasPermission('settings.users.view')" command="users">
                  <el-icon><UserFilled /></el-icon>
                  Користувачі
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  Налаштування
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  Вийти
                </el-dropdown-item>
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
            Увага! Дохід ФОП наближається до ліміту: <strong>{{ incomePercentage }}%</strong>. Решту ліміту: <strong>{{ formatCurrency(remainingLimit) }} грн</strong>.
        </div>
        
        <TabsBar />
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

  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useDark, useToggle } from '@vueuse/core'
import api from '@/api'

import TabsBar from '@/components/layout/TabsBar.vue'
import CallResultDialog from '@/components/crm/CallResultDialog.vue'
import { useNotificationStore } from '@/stores/notification'

import {
  HomeFilled,
  Box,
  ShoppingCart,
  Briefcase,
  Wallet,
  DataAnalysis,
  Setting,
  Fold,
  Expand,
  Bell,
  User,
  UserFilled,
  SwitchButton,
  Monitor,
  Tools,
  Tickets,
  WarningFilled,
  Right,
  Check,
  ArrowRight
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()

// Notification grouping and actions
const groupedNotifications = computed(() => {
  const groups = {}
  const now = new Date()
  const todayStr = now.toLocaleDateString()
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  const yesterdayStr = yesterday.toLocaleDateString()
  
  notificationStore.notifications.forEach(n => {
    const d = new Date(n.created_at)
    const dateStr = d.toLocaleDateString()
    
    let key = 'РАНІШЕ'
    if (dateStr === todayStr) key = 'СЬОГОДНІ'
    else if (dateStr === yesterdayStr) key = 'ВЧОРА'
    
    if (!groups[key]) groups[key] = []
    groups[key].push(n)
  })
  return groups
})

const getPriorityClass = (type) => {
  if (['CALL', 'DEADLINE_OVERDUE'].includes(type)) return 'red'
  if (['DEADLINE_SOON', 'STALE_LEAD'].includes(type)) return 'yellow'
  if (type === 'SUCCESS') return 'green'
  return 'white'
}

const handleNotificationAction = (n) => {
  if (n.type === 'CALL') {
    currentCallTask.value = {
      id: n.data.task_id,
      order_id: n.data.real_order_id,
      order_number: n.data.order_number,
      client_phone: n.data.client_phone
    }
    callDialogVisible.value = true
  } else if (n.data?.order_id) {
    // Redirect to CRM editor as requested
    router.push({ name: 'crm-order-edit', params: { id: n.data.order_id } })
  }
}

const isCollapse = ref(false)
const sidebarWidth = computed(() => isCollapse.value ? '64px' : '230px')
const activeMenu = computed(() => route.path)

const isDark = useDark()
const toggleTheme = useToggle(isDark)

const currentRouteTitle = computed(() => {
  const match = route.matched.slice().reverse().find(r => r.meta && r.meta.title)
  return match ? match.meta.title : 'Головна'
})

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'users':
      router.push('/settings/users')
      break
    case 'settings':
      router.push('/settings')
      break
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

const hasOverdueCalls = computed(() => {
  return notificationStore.notifications.some(n => 
    (n.type === 'CALL' || n.type === 'DEADLINE_OVERDUE') && isOverdue(n)
  )
})

const isOverdue = (n) => {
  if (!n.created_at) return false
  return new Date(n.created_at) < new Date()
}

const formatTime = (ts) => {
  if (!ts) return ''
  const d = new Date(ts)
  return d.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}

// Tax Warning Logic
const taxWarningVisible = ref(false)
const incomePercentage = ref(0)
const remainingLimit = ref(0)

onMounted(async () => {
    // Start notifications
    notificationStore.startPolling()

    try {
        const res = await api.get('/api/v1/finance/fop-income')
        if (res.data) {
            incomePercentage.value = res.data.percentage
            remainingLimit.value = res.data.remaining
            // Show red banner ONLY if > 95%
            if (incomePercentage.value >= 95) {
                taxWarningVisible.value = true
            }
        }
    } catch (e) {
        console.error('Failed to check tax limit', e)
    }
})

onBeforeUnmount(() => {
    notificationStore.stopPolling()
})

const formatCurrency = (v) => Number(v || 0).toLocaleString('uk-UA')
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
}

.sidebar {
  background-color: var(--sidebar-bg, #ffffff);
  border-right: 1px solid var(--el-border-color-light);
  transition: width 0.3s, background-color 0.3s;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-scrollbar {
  flex: 1;
  overflow: hidden;
}

html.dark .sidebar {
  --sidebar-bg: #0f172a; /* Deep navy for dark mode */
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: transparent;
  color: var(--el-text-color-primary);
  border-bottom: 1px solid var(--el-border-color-light);
  transition: all 0.3s;
}

html.dark .logo {
  color: #ffffff;
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  white-space: nowrap;
}

.el-menu {
  border: none;
  background-color: transparent;
}

.custom-sidebar-menu {
  --sidebar-hover-bg: rgba(0, 0, 0, 0.04);
}

html.dark .custom-sidebar-menu {
  --sidebar-hover-bg: rgba(255, 255, 255, 0.05);
}

.custom-sidebar-menu :deep(.el-menu-item),
.custom-sidebar-menu :deep(.el-sub-menu__title) {
  color: var(--el-text-color-regular);
  margin: 4px 8px;
  border-radius: 8px;
  height: 48px;
  line-height: normal;
  display: flex !important;
  align-items: center;
  font-size: 15px;
  font-weight: 500;
  position: relative;
  box-sizing: border-box;
}

/* Обрізаємо довгий текст трьома крапками, якщо сайдбар вузький */
.custom-sidebar-menu :deep(.el-menu-item span),
.custom-sidebar-menu :deep(.el-sub-menu__title span) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
  margin-left: 8px;
}

/* Fix submenu arrow (chevron) alignment */
.custom-sidebar-menu :deep(.el-sub-menu__icon-arrow) {
  position: absolute;
  right: 12px;
  top: 50%;
  margin-top: -7px; /* Center perfectly vertically */
  font-size: 14px;
}

/* Disable all collapse/expand animations per user request to avoid layout shifts */
.custom-sidebar-menu :deep(.el-menu--inline) {
  background-color: transparent !important;
  position: relative;
  transition: none !important;
}

.custom-sidebar-menu :deep(.el-collapse-transition) {
  transition: none !important;
  display: block !important;
}

.custom-sidebar-menu :deep(.el-sub-menu__title) {
  transition: none !important;
}

/* Tree-line left border */
.custom-sidebar-menu :deep(.el-menu--inline::before) {
  content: '';
  position: absolute;
  left: 31px; /* Align deeply with the parent icon / text padding */
  top: 0;
  bottom: 12px;
  width: 1px;
  background-color: var(--el-border-color-lighter);
  z-index: 1;
}

html.dark .custom-sidebar-menu :deep(.el-menu--inline::before) {
  background-color: rgba(255, 255, 255, 0.1);
}

.custom-sidebar-menu :deep(.el-menu-item:hover),
.custom-sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: var(--sidebar-hover-bg) !important;
  color: var(--el-text-color-primary);
}

/* Match active color for the chevron/sub-menu title when active in light mode */
.custom-sidebar-menu :deep(.el-sub-menu.is-active > .el-sub-menu__title) {
  color: #4f46e5 !important;
  font-weight: 600;
}

html.dark .custom-sidebar-menu :deep(.el-sub-menu.is-active > .el-sub-menu__title) {
  color: #a78bfa !important;
}

/* Global overrides for element-plus teleported popup menus */
:global(.el-menu--popup) {
  background-color: var(--sidebar-bg, #ffffff) !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
  padding: 6px !important;
  min-width: 180px;
}

:global(html.dark .el-menu--popup) {
  background-color: #0f172a !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1) !important;
}

:global(.el-menu--popup .el-menu-item) {
  margin: 2px 4px !important;
  border-radius: 6px !important;
  height: 40px !important;
  line-height: 40px !important;
  color: var(--el-text-color-regular) !important;
}

:global(.el-menu--popup .el-menu-item:hover) {
  background-color: var(--el-fill-color-light) !important;
  color: var(--el-text-color-primary) !important;
}

:global(html.dark .el-menu--popup .el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.05) !important;
}

/* Custom modern active state for sidebar (Light Mode) */
.custom-sidebar-menu :deep(.el-menu-item.is-active),
:global(.el-menu--popup .el-menu-item.is-active) {
  background-color: rgba(99, 102, 241, 0.1) !important;
  color: #4f46e5 !important;
  box-shadow: inset -3px 0 0 0 #6366f1 !important;
  border-right: none !important;
  position: relative;
  font-weight: 500;
}

.custom-sidebar-menu :deep(.el-menu-item.is-active::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background-color: #6366f1;
  border-radius: 0 4px 4px 0;
}

/* Dark Mode overrides for active state */
html.dark .custom-sidebar-menu :deep(.el-menu-item.is-active),
:global(html.dark .el-menu--popup .el-menu-item.is-active) {
  background-color: rgba(99, 102, 241, 0.15) !important;
  color: #a78bfa !important;
  box-shadow: inset -3px 0 0 0 #8b5cf6 !important;
  border-right: none !important;
}

html.dark .custom-sidebar-menu :deep(.el-menu-item.is-active::before) {
  background-color: #8b5cf6;
}

.top-header {
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.top-page-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-avatar {
  cursor: pointer;
}

.user-info {
  padding: 8px 0;
}

.user-name {
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.user-email {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.main-content {
  background-color: var(--el-bg-color-page);
  padding: 0;
  display: flex;
  flex-direction: column;
}

.theme-toggle-btn {
  font-size: 16px;
  border-color: var(--el-border-color-light);
}

/* Notifications Styles */
.notification-badge :deep(.el-badge__content) {
  top: 5px;
  right: 5px;
}

.bell-ringing {
  animation: ring 2s infinite;
  color: #ef4444 !important;
  border-color: #ef4444 !important;
}

@keyframes ring {
  0% { transform: rotate(0); }
  10% { transform: rotate(15deg); }
  20% { transform: rotate(-15deg); }
  30% { transform: rotate(10deg); }
  40% { transform: rotate(-10deg); }
  50% { transform: rotate(0); }
  100% { transform: rotate(0); }
}

:global(.notification-popover) {
  padding: 0 !important;
  border-radius: 12px !important;
  overflow: hidden;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1) !important;
}

.notification-panel {
  display: flex;
  flex-direction: column;
}

.notification-header {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color);
}

.notification-groups {
  padding: 0;
}

.group-header {
  padding: 8px 16px;
  background: var(--el-fill-color-lighter);
  font-size: 11px;
  font-weight: 700;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.notification-item {
  display: flex;
  padding: 14px 16px;
  gap: 12px;
  border-bottom: 1px solid var(--el-border-color-extra-light);
  transition: all 0.2s;
  cursor: default;
  position: relative;
}

.notification-item:hover {
  background: var(--el-fill-color-light);
}

.notification-item.is-urgent {
  background: rgba(239, 68, 68, 0.03);
}

.ni-dot {
  width: 8px;
  height: 8px;
  min-width: 8px;
  border-radius: 50%;
  margin-top: 6px;
}

.priority-red { background-color: #ef4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }
.priority-yellow { background-color: #f59e0b; }
.priority-green { background-color: #10b981; }
.priority-white { background-color: #9ca3af; }

.ni-content {
  flex: 1;
  min-width: 0;
}

.ni-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 3px;
  line-height: 1.4;
  color: var(--el-text-color-primary);
}

.ni-time {
  color: #ef4444;
  font-weight: 700;
}

.ni-message {
  font-size: 12px;
  color: var(--el-text-color-regular);
  margin-bottom: 3px;
  line-height: 1.4;
}

.ni-phone {
  font-size: 11px;
  color: #4f46e5;
  font-weight: 600;
}

.ni-actions {
  display: flex;
  align-items: center;
  margin-left: 8px;
}

.action-btn {
  opacity: 0.6;
  border: none;
  background: transparent;
  transition: all 0.2s;
}

.action-btn:hover {
  opacity: 1;
  background: var(--el-fill-color);
  transform: translateX(2px);
}

.empty-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
  opacity: 0.5;
}

.view-container {
  padding: 20px;
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.tax-limit-warning-banner {
    background-color: #ef4444;
    color: white;
    padding: 10px 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    z-index: 1000;
    animation: slideIn 0.3s ease;
}

.tax-limit-warning-banner strong {
    margin-left: 5px;
    margin-right: 5px;
}

@keyframes slideIn {
    from { transform: translateY(-100%); }
    to { transform: translateY(0); }
}

.mr-2 { margin-right: 8px; }
</style>

