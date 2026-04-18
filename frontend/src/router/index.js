import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

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
            path: '/forgot-password',
            name: 'forgot-password',
            component: () => import('@/views/auth/ForgotPasswordView.vue'),
            meta: { requiresAuth: false }
        },
        // ─── Calculator (public, no auth required) ───────────────────────
        {
            path: '/calculator',
            name: 'calculator',
            component: () => import('@/views/Calculator/DrawerCalculator.vue'),
            meta: { requiresAuth: false }
        },
        {
            path: '/calculator/admin',
            name: 'calculator-admin',
            component: () => import('@/views/Calculator/CalculatorAdmin.vue'),
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
                    path: '/settings/numbering',
                    name: 'system-numbering',
                    component: () => import('@/views/Settings/DocumentSequences.vue'),
                    meta: { requiresAuth: true, title: 'Нумерація документів', permission: 'admin.all' }
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
                    meta: { requiresAuth: true, title: 'Організація', permission: 'admin.all' }
                },
                // Inventory routes
                {
                    path: '/inventory/nomenclature',
                    name: 'nomenclature',
                    component: () => import('@/views/Inventory/Nomenclature.vue'),
                    meta: { title: 'Номенклатура', permission: 'inventory.nomenclature.view' }
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
                    component: () => import('@/views/Sales/CounterpartiesList.vue'),
                    meta: { title: 'Контрагенти' }
                },
                {
                    path: '/sales/counterparties/new',
                    name: 'counterparty-new',
                    component: () => import('@/views/Sales/CounterpartyEditor.vue'),
                    meta: { title: 'Новий контрагент' }
                },
                {
                    path: '/sales/counterparties/:id',
                    name: 'counterparty-edit',
                    component: () => import('@/views/Sales/CounterpartyEditor.vue'),
                    meta: { title: 'Контрагент' }
                },
                {
                    path: '/sales/orders',
                    name: 'sales-orders',
                    component: () => import('@/views/Sales/OrdersList.vue'),
                    meta: { title: 'Замовлення (Продаж)', permission: 'sales.orders.view' }
                },
                {
                    path: '/sales/orders/new',
                    name: 'sales-order-new',
                    component: () => import('@/views/Sales/OrderEditor.vue'),
                    meta: { title: 'Нове замовлення' }
                },
                {
                    path: '/sales/orders/:id',
                    name: 'sales-order-edit',
                    component: () => import('@/views/Sales/OrderEditor.vue'),
                    meta: { title: 'Редагування замовлення' }
                },
                {
                    path: '/sales/invoices',
                    name: 'sales-invoices',
                    component: () => import('@/views/Sales/InvoicesList.vue'),
                    meta: { title: 'Видаткові накладні' }
                },
                {
                    path: '/sales/invoices/new',
                    name: 'sales-invoice-new',
                    component: () => import('@/views/Sales/InvoiceEditor.vue'),
                    meta: { title: 'Нова накладна' }
                },
                {
                    path: '/sales/invoices/:id',
                    name: 'sales-invoice-edit',
                    component: () => import('@/views/Sales/InvoiceEditor.vue'),
                    meta: { title: 'Редагування накладної', permission: 'sales.invoices.view' }
                },
                // Purchase routes
                {
                    path: '/purchases/orders',
                    name: 'purchase-orders',
                    component: () => import('@/views/Purchases/PurchaseOrderList.vue'),
                    meta: { title: 'Замовлення постачальникам' }
                },
                {
                    path: '/purchases/orders/new',
                    name: 'purchase-order-new',
                    component: () => import('@/views/Purchases/PurchaseOrderEditor.vue'),
                    meta: { title: 'Нове замовлення' }
                },
                {
                    path: '/purchases/orders/:id',
                    name: 'purchase-order-edit',
                    component: () => import('@/views/Purchases/PurchaseOrderEditor.vue'),
                    meta: { title: 'Редагування замовлення' }
                },
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
                // Production routes
                {
                    path: '/production/orders',
                    name: 'production-orders',
                    component: () => import('@/views/Production/ProductionOrdersList.vue'),
                    meta: { title: 'Завдання на виробництво' }
                },
                {
                    path: '/production/orders/new',
                    name: 'production-order-new',
                    component: () => import('@/views/Production/ProductionOrderEditor.vue'),
                    meta: { title: 'Нове завдання' }
                },
                {
                    path: '/production/orders/:id',
                    name: 'production-order-edit',
                    component: () => import('@/views/Production/ProductionOrderEditor.vue'),
                    meta: { title: 'Редагування завдання' }
                },
                // CRM routes
                {
                    path: '/crm',
                    name: 'crm-board',
                    component: () => import('@/views/CRM/CrmOrdersBoard.vue'),
                    meta: { title: 'CRM — Замовлення' }
                },
                {
                    path: '/crm/orders/new',
                    name: 'crm-order-new',
                    component: () => import('@/views/CRM/CrmOrderEditor.vue'),
                    meta: { title: 'Нова заявка CRM' }
                },
                {
                    path: '/crm/orders/:id',
                    name: 'crm-order-edit',
                    component: () => import('@/views/CRM/CrmOrderEditor.vue'),
                    meta: { title: 'CRM — Замовлення' }
                },
                // Settings
                {
                    path: '/settings/users',
                    name: 'users',
                    component: () => import('@/views/Settings/Users.vue'),
                    meta: { title: 'Користувачі', permission: 'settings.users.view' }
                },
                {
                    path: '/settings/trash-bin',
                    name: 'trash-bin',
                    component: () => import('@/views/Admin/TrashBin.vue'),
                    meta: { title: 'Корзина', permission: 'settings.view' }
                },
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
            // Check granular permissions
            const requiredPermission = to.meta.permission
            if (requiredPermission && !userStore.hasPermission(requiredPermission)) {
                ElMessage.error('Доступ заборонено')
                next('/dashboard')
            } else {
                next()
            }
        }
    } else {
        next()
    }
})

export default router
