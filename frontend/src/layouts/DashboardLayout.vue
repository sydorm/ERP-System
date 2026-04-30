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
          <el-menu-item index="/inventory/nomenclature" v-if="userStore.hasPermission('inventory.nomenclature.view')">
            <span class="dot-indicator"></span>Номенклатура
          </el-menu-item>
          <el-menu-item index="/inventory/warehouses" v-if="userStore.hasPermission('inventory.warehouses.view')">
            <span class="dot-indicator"></span>Склади
          </el-menu-item>
          <el-menu-item index="/inventory/stock" v-if="userStore.hasPermission('inventory.stock.view')">
            <span class="dot-indicator"></span>Залишки
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="crm">
          <template #title>
            <el-icon><Tickets /></el-icon>
            <span>CRM</span>
          </template>
          <el-menu-item index="/crm">
            <span class="dot-indicator"></span>Замовлення
          </el-menu-item>
          <el-menu-item index="/crm/analytics">
            <span class="dot-indicator"></span>Аналітика
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="sales" v-if="userStore.hasPermission('sales.view')">
          <template #title>
            <el-icon><ShoppingCart /></el-icon>
            <span>Продажі</span>
          </template>
          <el-menu-item index="/sales/counterparties" v-if="userStore.hasPermission('sales.counterparties.view')">
            <span class="dot-indicator"></span>Контрагенти
          </el-menu-item>
          <el-menu-item index="/sales/orders" v-if="userStore.hasPermission('sales.orders.view')">
            <span class="dot-indicator"></span>Замовлення
          </el-menu-item>
          <el-menu-item index="/sales/invoices" v-if="userStore.hasPermission('sales.invoices.view')">
            <span class="dot-indicator"></span>Рахунки
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="purchases" v-if="userStore.hasPermission('purchases.view')">
          <template #title>
            <el-icon><Briefcase /></el-icon>
            <span>Закупівлі</span>
          </template>
          <el-menu-item index="/purchases/orders" v-if="userStore.hasPermission('purchases.orders.view')">
            <span class="dot-indicator"></span>Замовлення
          </el-menu-item>
          <el-menu-item index="/purchases/planning">
            <span class="dot-indicator"></span>Планування
          </el-menu-item>
          <el-menu-item index="/purchases/receipts" v-if="userStore.hasPermission('purchases.receipts.view')">
            <span class="dot-indicator"></span>Прибуткові накладні
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="production">
          <template #title>
            <el-icon><Tools /></el-icon>
            <span>Виробництво</span>
          </template>
          <el-menu-item index="/production/orders">
            <span class="dot-indicator"></span>Завдання
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="finance" v-if="userStore.hasPermission('finance.view')">
          <template #title>
            <el-icon><Wallet /></el-icon>
            <span>Фінанси</span>
          </template>
          <el-menu-item index="/finance/cash" v-if="userStore.hasPermission('finance.cash.view')">
            <span class="dot-indicator"></span>Каса
          </el-menu-item>
          <el-menu-item index="/finance/bank" v-if="userStore.hasPermission('finance.bank.view')">
            <span class="dot-indicator"></span>Банк
          </el-menu-item>
          <el-menu-item index="/finance/payments" v-if="userStore.hasPermission('finance.payments.view')">
            <span class="dot-indicator"></span>Платежі
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="personnel">
          <template #title>
            <el-icon><User /></el-icon>
            <span>Персонал</span>
          </template>
          <el-menu-item index="/personnel/employees">
            <span class="dot-indicator"></span>Співробітники
          </el-menu-item>
          <el-menu-item index="/personnel/departments">
            <span class="dot-indicator"></span>Підрозділи
          </el-menu-item>
          <el-menu-item index="/personnel/payroll">
            <span class="dot-indicator"></span>Нарахування ЗП
          </el-menu-item>
          <el-menu-item index="/personnel/attendance">
            <span class="dot-indicator"></span>Табель
          </el-menu-item>
          <el-menu-item index="/personnel/hr-reports">
            <span class="dot-indicator"></span>Звіти по ЗП
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/reports" v-if="userStore.hasPermission('reports.view')">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>Звіти</template>
        </el-menu-item>

        <el-sub-menu index="admin" v-if="hasAdministrationAccess">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>Адміністрування</span>
          </template>
          <el-menu-item index="/settings/company" v-if="userStore.hasPermission('settings.manage')">
            <span class="dot-indicator"></span>Організація
          </el-menu-item>
          <el-menu-item index="/settings/dictionaries" v-if="userStore.hasPermission('dictionaries.view')">
            <span class="dot-indicator"></span>Довідники
          </el-menu-item>
          <el-menu-item index="/settings/print-templates" v-if="userStore.hasPermission('print_templates.view')">
            <span class="dot-indicator"></span>Шаблони документів
          </el-menu-item>
          <el-menu-item index="/settings/business-process-rules" v-if="userStore.hasPermission('business_processes.view')">
            <span class="dot-indicator"></span>Бізнес-процеси
          </el-menu-item>
          <el-menu-item index="/settings/trash-bin" v-if="userStore.hasPermission('settings.view')">
            <span class="dot-indicator"></span>Корзина
          </el-menu-item>
        </el-sub-menu>
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
            class="sidebar-toggle"
          />
          <div class="global-search-container">
            <el-input
              placeholder="Пошук у системі..."
              :prefix-icon="Search"
              clearable
              class="erp-global-search"
            />
          </div>
          <TabsBar class="header-tabs" />
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
              <el-avatar :size="32">
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
                <el-dropdown-item v-if="userStore.hasPermission('users.view')" command="users">
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
  ArrowRight,
  Search
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
const sidebarWidth = computed(() => isCollapse.value ? '64px' : '250px')
const activeMenu = computed(() => route.path)
const hasAdministrationAccess = computed(() => [
  'settings.view',
  'settings.manage',
  'dictionaries.view',
  'print_templates.view',
  'business_processes.view',
  'users.view',
].some(permission => userStore.hasPermission(permission)))

const isDark = useDark()
const toggleTheme = useToggle(isDark)

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
  background: var(--erp-sidebar-bg);
  border-right: 1px solid var(--erp-sidebar-border);
  transition: width 0.3s;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  z-index: 200;
}

.sidebar-scrollbar {
  flex: 1;
  overflow: hidden;
}

.logo {
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background-color: transparent;
  color: var(--erp-text-heading);
  border-bottom: 1px solid var(--erp-sidebar-border);
  transition: all 0.3s;
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.5px;
  white-space: nowrap;
}

.custom-sidebar-menu {
  border: none;
  background: transparent;
}

.custom-sidebar-menu :deep(.el-menu-item),
.custom-sidebar-menu :deep(.el-sub-menu__title) {
  color: var(--erp-sidebar-text) !important;
  margin: 4px 12px;
  border-radius: var(--erp-radius-btn);
  height: 44px;
  line-height: normal;
  display: flex !important;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
  position: relative;
  transition: all 0.2s;
}

.custom-sidebar-menu :deep(.el-menu-item:hover),
.custom-sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: #F8FAFC !important;
  color: var(--erp-text-heading) !important;
}

.custom-sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: var(--erp-sidebar-active-bg) !important;
  color: var(--erp-sidebar-active-text) !important;
  font-weight: 600;
}

.custom-sidebar-menu :deep(.el-menu-item.is-active::before) {
  content: '';
  position: absolute;
  left: -12px;
  top: 8px;
  bottom: 8px;
  width: 4px;
  background-color: var(--erp-sidebar-active-text);
  border-radius: 0 4px 4px 0;
}

.dot-indicator {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: #CBD5E1;
  margin-right: 12px;
  display: inline-block;
  transition: background-color 0.2s;
}

.el-menu-item.is-active .dot-indicator {
  background-color: var(--erp-sidebar-active-text);
  box-shadow: 0 0 8px var(--erp-sidebar-active-text);
}

.top-header {
  background-color: #FFFFFF;
  border-bottom: 1px solid var(--erp-sidebar-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 64px;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.sidebar-toggle {
  border: none;
  background: transparent;
  font-size: 20px;
  color: var(--erp-text-muted);
}

.global-search-container {
  margin-left: 20px;
  width: 320px;
}

.erp-global-search :deep(.el-input__wrapper) {
  background-color: #F8FAFC;
  box-shadow: none !important;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  padding: 0 12px;
}

.erp-global-search :deep(.el-input__inner) {
  height: 38px;
  font-size: 14px;
}

.header-tabs {
  flex: 1;
  min-width: 0;
  margin-left: 24px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right :deep(.el-button) {
  border-color: #E2E8F0;
  color: var(--erp-text-muted);
}

.user-avatar {
  cursor: pointer;
  margin-left: 8px;
}

.main-content {
  background-color: var(--erp-bg-page);
  padding: 0;
  display: flex;
  flex-direction: column;
}

.view-container {
  flex: 1;
  padding: 24px;
}
</style>
