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

          <el-sub-menu index="crm">
            <template #title>
              <el-icon><Tickets /></el-icon>
              <span>CRM</span>
            </template>
            <el-menu-item index="/crm">Замовлення</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="sales">
            <template #title>
              <el-icon><ShoppingCart /></el-icon>
              <span>Продажі</span>
            </template>
            <el-menu-item index="/sales/counterparties">Контрагенти</el-menu-item>
            <el-menu-item index="/sales/orders">Замовлення</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="purchases">
            <template #title>
              <el-icon><Briefcase /></el-icon>
              <span>Закупівлі</span>
            </template>
            <el-menu-item index="/purchases/orders">Замовлення постачальникам</el-menu-item>
            <el-menu-item index="/purchases/planning">Планування</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="inventory">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>Склад</span>
            </template>
            <el-menu-item index="/inventory/nomenclature">Номенклатура</el-menu-item>
            <el-menu-item index="/inventory/warehouses">Склади</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="production">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>Виробництво</span>
            </template>
            <el-menu-item index="/production/orders">Завдання</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="finance">
            <template #title>
              <el-icon><Wallet /></el-icon>
              <span>Фінанси</span>
            </template>
            <el-menu-item index="/finance/cash">Каса</el-menu-item>
            <el-menu-item index="/finance/bank">Банк</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/reports">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>Звіти та аналітика</template>
          </el-menu-item>

          <el-menu-item index="/automation">
            <el-icon><Cpu /></el-icon>
            <template #title>Автоматизація</template>
          </el-menu-item>

          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <template #title>Налаштування</template>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>

      <!-- Sidebar Bottom -->
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

    <!-- Main Content -->
    <el-container>
      <!-- Top Header -->
      <el-header class="top-header">
        <div class="header-left">
          <el-button link class="home-btn"><el-icon><HomeFilled /></el-icon></el-button>
        </div>

        <div class="header-center">
          <div class="global-search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <input type="text" placeholder="Пошук у системі..." />
            <div class="search-shortcut">⌘ K</div>
          </div>
        </div>

        <div class="header-right">
          <el-badge :value="6" class="header-badge">
            <el-button circle link><el-icon><Bell /></el-icon></el-button>
          </el-badge>
          <el-badge :value="2" class="header-badge">
            <el-button circle link><el-icon><ChatDotRound /></el-icon></el-button>
          </el-badge>
          <el-button circle link><el-icon><QuestionFilled /></el-icon></el-button>
          
          <div class="user-profile">
            <div class="user-meta">
              <div class="user-name">{{ userStore.user?.firstName || 'Андрій' }} {{ userStore.user?.lastName || 'Коваль' }}</div>
              <div class="user-role">Директор</div>
            </div>
            <el-avatar :size="36" src="https://i.pravatar.cc/150?u=a042581f4e29026704d" />
          </div>
        </div>
      </el-header>

      <!-- Main Content Area -->
      <el-main class="main-content">
        <div class="view-container">
          <router-view v-slot="{ Component }">
            <keep-alive>
              <component :is="Component" :key="route.path" />
            </keep-alive>
          </router-view>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useDark, useToggle } from '@vueuse/core'
import api from '@/api'
import {
  HomeFilled, Box, ShoppingCart, Briefcase, Wallet, DataAnalysis, Setting,
  Fold, Expand, Bell, User, UserFilled, SwitchButton, Tools, Tickets,
  Monitor, Search, QuestionFilled, ChatDotRound, Lightning, Sunny, Moon, Cpu
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)
const sidebarWidth = computed(() => isCollapse.value ? '64px' : '260px')
const activeMenu = computed(() => route.path)

const isDark = useDark()
const toggleTheme = useToggle(isDark)

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  background-color: var(--erp-bg-page);
}

/* Sidebar */
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

.logo h2 span {
  color: var(--erp-primary);
}

.custom-sidebar-menu {
  border: none;
  background: transparent;
}

.custom-sidebar-menu :deep(.el-menu-item),
.custom-sidebar-menu :deep(.el-sub-menu__title) {
  color: var(--erp-sidebar-text) !important;
  margin: 2px 12px;
  border-radius: 10px;
  height: 40px;
  font-size: 14px;
  font-weight: 500;
}

.custom-sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: var(--erp-sidebar-active-bg) !important;
  color: var(--erp-primary) !important;
  font-weight: 600;
}

.sidebar-bottom {
  border-top: 1px solid var(--erp-sidebar-border);
  padding: 12px 0;
}

.bottom-menu {
  border: none;
  background: transparent;
}

.sidebar-footer {
  padding: 8px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--erp-text-muted);
  font-size: 14px;
}

/* Header */
.top-header {
  background: #FFFFFF;
  border-bottom: 1px solid var(--erp-sidebar-border);
  display: grid;
  grid-template-columns: 100px 1fr 350px;
  align-items: center;
  padding: 0 24px;
  height: 64px;
}

.home-btn {
  font-size: 20px;
  color: var(--erp-text-muted);
}

.header-center {
  display: flex;
  justify-content: center;
}

.global-search-box {
  width: 480px;
  height: 40px;
  background: #F1F5F9;
  border-radius: 12px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 12px;
}

.global-search-box input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--erp-text-main);
}

.search-shortcut {
  font-size: 12px;
  color: var(--erp-text-muted);
  border: 1px solid #CBD5E1;
  border-radius: 4px;
  padding: 2px 6px;
  background: #FFF;
}

.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 20px;
}

.header-badge :deep(.el-badge__content) {
  background-color: var(--erp-primary);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.user-meta {
  text-align: right;
}

.user-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--erp-text-heading);
}

.user-role {
  font-size: 12px;
  color: var(--erp-text-muted);
}

.main-content {
  padding: 0;
}

.view-container {
  padding: 32px;
}
</style>
