<template>
  <el-container class="dashboard-container">
    <!-- Sidebar -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="logo">
        <h2 v-if="!isCollapse">ERP System</h2>
        <h2 v-else>ERP</h2>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :router="true"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <template #title>Головна</template>
        </el-menu-item>

        <el-sub-menu index="inventory">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>Склад</span>
          </template>
          <el-menu-item index="/inventory/nomenclature">Номенклатура</el-menu-item>
          <el-menu-item index="/inventory/warehouses">Склади</el-menu-item>
          <el-menu-item index="/inventory/stock">Залишки</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="sales">
          <template #title>
            <el-icon><ShoppingCart /></el-icon>
            <span>Продажі</span>
          </template>
          <el-menu-item index="/sales/counterparties">Контрагенти</el-menu-item>
          <el-menu-item index="/sales/orders">Замовлення</el-menu-item>
          <el-menu-item index="/sales/invoices">Рахунки</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="purchasing">
          <template #title>
            <el-icon><Briefcase /></el-icon>
            <span>Закупівлі</span>
          </template>
          <el-menu-item index="/purchasing/orders">Замовлення</el-menu-item>
          <el-menu-item index="/purchasing/receipts">Прибуткові накладні</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="finance">
          <template #title>
            <el-icon><Wallet /></el-icon>
            <span>Фінанси</span>
          </template>
          <el-menu-item index="/finance/cash">Каса</el-menu-item>
          <el-menu-item index="/finance/bank">Банк</el-menu-item>
          <el-menu-item index="/finance/payments">Платежі</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/reports">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>Звіти</template>
        </el-menu-item>

        <!-- Administration Section -->
        <el-sub-menu index="admin" v-if="userStore.user?.role === 'admin'">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>Адміністрування</span>
          </template>
          <el-menu-item index="/settings/dictionaries">Довідники</el-menu-item>
          <el-menu-item index="/settings/users">Користувачі</el-menu-item>
        </el-sub-menu>

        <!-- Settings submenu removed as Users moved to profile dropdown -->
      </el-menu>
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
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">Головна</el-breadcrumb-item>
            <el-breadcrumb-item v-for="item in breadcrumbItems" :key="item">
              {{ item }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-button :icon="Bell" circle />
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
                <el-dropdown-item v-if="userStore.user?.role === 'admin'" command="users">
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
        <router-view />
      </el-main>
    </el-container>

    <!-- AI Assistant Component -->
    <AiAssistant />
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import AiAssistant from '@/components/AiAssistant.vue'
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
  SwitchButton
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)
const sidebarWidth = computed(() => isCollapse.value ? '64px' : '200px')
const activeMenu = computed(() => route.path)

const breadcrumbItems = computed(() => {
  const pathArray = route.path.split('/').filter(item => item)
  return pathArray.slice(1) // Remove first item (already in breadcrumb)
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
      userStore.logout()
      ElMessage.success('Ви вийшли з системи')
      router.push('/login')
      break
  }
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow-x: hidden;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #263445;
  color: white;
  transition: all 0.3s;
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  white-space: nowrap;
}

.el-menu {
  border: none;
}

.top-header {
  background-color: white;
  border-bottom: 1px solid #e6e6e6;
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
  color: #303133;
  margin-bottom: 4px;
}

.user-email {
  font-size: 12px;
  color: #909399;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
