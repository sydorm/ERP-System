import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            redirect: '/dashboard'
        },
        {
            path: '/login',
            name: 'login',
            component: () => import('@/views/auth/LoginView.vue'),
            meta: { requiresAuth: false }
        },
        {
            path: '/signup',
            name: 'signup',
            component: () => import('@/views/auth/SignupView.vue'),
            meta: { requiresAuth: false }
        },
        {
            path: '/dashboard',
            component: () => import('@/layouts/DashboardLayout.vue'),
            meta: { requiresAuth: true },
            children: [
                {
                    path: '',
                    name: 'dashboard',
                    component: () => import('@/views/DashboardHome.vue'),
                    meta: { title: 'Головна' }
                },
                {
                    path: '/profile',
                    name: 'profile',
                    component: () => import('@/views/Profile.vue'),
                    meta: { title: 'Профіль' }
                },
                {
                    path: '/settings/dictionaries',
                    name: 'dictionaries',
                    component: () => import('@/views/Settings/Dictionaries.vue'),
                    meta: { requiresAuth: true, title: 'Довідники' }
                },
                {
                    path: '/settings/company',
                    name: 'company-settings',
                    component: () => import('@/views/Settings/CompanySettings.vue'),
                    meta: { requiresAuth: true, title: 'Організація' }
                },
                // Inventory routes
                {
                    path: '/inventory/nomenclature',
                    name: 'nomenclature',
                    component: () => import('@/views/Inventory/Nomenclature.vue'),
                    meta: { title: 'Номенклатура' }
                },
                {
                    path: '/inventory/nomenclature/new',
                    name: 'product-new',
                    component: () => import('@/views/Inventory/ProductEditor.vue'),
                    meta: { title: 'Новий товар' }
                },
                {
                    path: '/inventory/nomenclature/:id',
                    name: 'product-edit',
                    component: () => import('@/views/Inventory/ProductEditor.vue'),
                    meta: { title: 'Редагування товару' }
                },
                {
                    path: '/inventory/warehouses',
                    name: 'warehouses',
                    component: () => import('@/views/HomeView.vue'), // Placeholder
                    meta: { title: 'Склади' }
                },
                // Sales routes
                {
                    path: '/sales/counterparties',
                    name: 'counterparties',
                    component: () => import('@/views/HomeView.vue'), // Placeholder
                    meta: { title: 'Контрагенти' }
                },
                {
                    path: '/sales/orders',
                    name: 'sales-orders',
                    component: () => import('@/views/HomeView.vue'), // Placeholder
                    meta: { title: 'Замовлення (Продаж)' }
                },
                // Purchase routes
                {
                    path: '/purchases/receipts',
                    name: 'purchase-receipts',
                    component: () => import('@/views/Purchases/PurchaseReceiptsList.vue'),
                    meta: { title: 'Прибуткові накладні' }
                },
                {
                    path: '/purchases/receipts/new',
                    name: 'purchase-receipt-new',
                    component: () => import('@/views/Purchases/PurchaseReceiptEditor.vue'),
                    meta: { title: 'Нова накладна' }
                },
                {
                    path: '/purchases/receipts/:id',
                    name: 'purchase-receipt-edit',
                    component: () => import('@/views/Purchases/PurchaseReceiptEditor.vue'),
                    meta: { title: 'Редагування накладної' }
                },
                // Settings
                {
                    path: '/settings/users',
                    name: 'users',
                    component: () => import('@/views/Settings/Users.vue'),
                    meta: { title: 'Користувачі' }
                }
            ]
        }
    ]
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
    const userStore = useUserStore()
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
    const isAuthenticated = userStore.isAuthenticated()

    if (requiresAuth && !isAuthenticated) {
        next('/login')
    } else if (isAuthenticated) {
        // If user is authenticated but profile is missing, fetch it
        if (!userStore.user) {
            await userStore.fetchUser()
        }

        if (!requiresAuth && (to.path === '/login' || to.path === '/signup')) {
            next('/dashboard')
        } else {
            next()
        }
    } else {
        next()
    }
})

export default router
