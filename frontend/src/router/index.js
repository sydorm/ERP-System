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
                    component: () => import('@/views/Dashboard/Index.vue'),
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
                    meta: { requiresAuth: true, title: 'Довідники', permission: 'dictionaries.view' }
                },
                {
                    path: '/settings/company',
                    name: 'company-settings',
                    component: () => import('@/views/Settings/CompanySettings.vue'),
                    meta: { requiresAuth: true, title: 'Організація', permission: 'settings.manage' }
                },
                {
                    path: '/settings/print-templates',
                    name: 'print-templates',
                    component: () => import('@/views/Settings/PrintTemplatesList.vue'),
                    meta: { requiresAuth: true, title: 'Шаблони документів', permission: 'print_templates.view' }
                },
                {
                    path: '/settings/print-templates/new',
                    name: 'print-template-new',
                    component: () => import('@/views/Settings/PrintTemplateEditor.vue'),
                    meta: { requiresAuth: true, title: 'Новий шаблон', permission: 'print_templates.create' }
                },
                {
                    path: '/settings/print-templates/:id',
                    name: 'print-template-edit',
                    component: () => import('@/views/Settings/PrintTemplateEditor.vue'),
                    meta: { requiresAuth: true, title: 'Редагування шаблону', permission: 'print_templates.edit' }
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
                    component: () => import('@/views/Inventory/Warehouses.vue'),
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
                    path: '/purchases',
                    component: () => import('@/views/Purchases/Purchases.vue'),
                    meta: { title: 'Закупівлі', requiresAuth: true },
                    children: [
                        {
                            path: '',
                            redirect: '/purchases/orders'
                        },
                        {
                            path: 'planning',
                            name: 'purchase-planning',
                            component: () => import('@/views/Purchases/PurchasesPlanning.vue'),
                            meta: { title: 'Планування' }
                        },
                        {
                            path: 'orders',
                            name: 'purchase-orders',
                            component: () => import('@/views/Purchases/PurchaseOrderList.vue'),
                            meta: { title: 'Замовлення' }
                        },
                        {
                            path: 'receipts',
                            name: 'purchase-receipts',
                            component: () => import('@/views/Purchases/PurchaseReceiptsList.vue'),
                            meta: { title: 'Прибуткові накладні' }
                        }
                    ]
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
                // Personnel routes
                {
                    path: '/personnel/employees',
                    name: 'employees-list',
                    component: () => import('@/views/Personnel/EmployeesList.vue'),
                    meta: { title: 'Співробітники', permission: 'personnel.view' }
                },
                {
                    path: '/personnel/employees/new',
                    name: 'employee-new',
                    component: () => import('@/views/Personnel/EmployeeEditor.vue'),
                    meta: { title: 'Новий співробітник', permission: 'personnel.create' }
                },
                {
                    path: '/personnel/employees/:id',
                    name: 'employee-edit',
                    component: () => import('@/views/Personnel/EmployeeEditor.vue'),
                    meta: { title: 'Картка співробітника', permission: 'personnel.view' }
                },
                {
                    path: '/personnel/departments',
                    name: 'departments-list',
                    component: () => import('@/views/Personnel/DepartmentsList.vue'),
                    meta: { title: 'Підрозділи', permission: 'personnel.view' }
                },
                {
                    path: '/personnel/payroll',
                    name: 'payroll-manager',
                    component: () => import('@/views/Personnel/PayrollManager.vue'),
                    meta: { title: 'Нарахування ЗП', permission: 'personnel.view' }
                },
                {
                    path: '/personnel/attendance',
                    name: 'attendance-board',
                    component: () => import('@/views/Personnel/AttendanceBoard.vue'),
                    meta: { title: 'Табель', permission: 'personnel.view' }
                },
                {
                    path: '/personnel/hr-reports',
                    name: 'payroll-reports',
                    component: () => import('@/views/Personnel/PayrollReports.vue'),
                    meta: { title: 'Звіти по ЗП' }
                },
                // CRM routes
                {
                    path: '/crm',
                    name: 'crm-board',
                    component: () => import('@/views/CRM/CrmOrdersBoard.vue'),
                    meta: { title: 'CRM' }
                },
                {
                    path: '/crm/analytics',
                    name: 'crm-analytics',
                    component: () => import('@/views/CRM/CrmInsights.vue'),
                    meta: { title: 'CRM — Аналітика', permission: 'crm.analytics' }
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
                {
                    path: '/crm/order-workspace/:id',
                    name: 'crm-order-workspace',
                    component: () => import('@/views/CRM/CrmOrderEditor.vue'),
                    meta: { title: 'Робочий простір заявки' }
                },
                {
                    path: '/crm/order-master/:id',
                    name: 'crm-order-master',
                    component: () => import('@/views/CRM/CrmOrderEditor.vue'),
                    meta: { title: 'Master Order Manager' }
                },
                // Settings
                {
                    path: '/settings/users',
                    name: 'users',
                    component: () => import('@/views/Settings/Users.vue'),
                    meta: { title: 'Користувачі', permission: 'users.view' }
                },
                {
                    path: '/settings/users/create',
                    name: 'user-create',
                    component: () => import('@/views/Settings/UserEditor.vue'),
                    meta: { title: 'Новий користувач', permission: 'users.create' }
                },
                {
                    path: '/settings/users/:id/edit',
                    name: 'user-edit',
                    component: () => import('@/views/Settings/UserEditor.vue'),
                    meta: { title: 'Редагування користувача', permission: 'users.edit' }
                },

                {
                    path: '/settings/business-process-rules',
                    name: 'business-process-rules',
                    component: () => import('@/views/Settings/BusinessProcessRules.vue'),
                    meta: { requiresAuth: true, title: 'Бізнес-процеси', permission: 'business_processes.view' }
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
            const isEditingSelf = to.name === 'user-edit' && String(to.params.id) === String(userStore.user?.id)
            const isSelfProfile = to.name === 'profile'

            if (requiredPermission && !userStore.hasPermission(requiredPermission) && !isEditingSelf && !isSelfProfile) {
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
