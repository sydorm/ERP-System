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
                    component: () => import('@/views/DashboardHome.vue')
                },
                {
                    path: '/profile',
                    name: 'profile',
                    component: () => import('@/views/Profile.vue')
                },
                {
                    path: '/settings/dictionaries',
                    name: 'dictionaries',
                    component: () => import('@/views/Settings/Dictionaries.vue'),
                    meta: { requiresAuth: true } // Should arguably be admin only, but let's keep it simple for now
                },
                // Inventory routes
                {
                    path: '/inventory/nomenclature',
                    name: 'nomenclature',
                    component: () => import('@/views/Inventory/Nomenclature.vue')
                },
                {
                    path: '/inventory/warehouses',
                    name: 'warehouses',
                    component: () => import('@/views/HomeView.vue') // Placeholder
                },
                // Sales routes
                {
                    path: '/sales/counterparties',
                    name: 'counterparties',
                    component: () => import('@/views/HomeView.vue') // Placeholder
                },
                {
                    path: '/sales/orders',
                    name: 'sales-orders',
                    component: () => import('@/views/HomeView.vue') // Placeholder
                },
                // Settings
                {
                    path: '/settings/users',
                    name: 'users',
                    component: () => import('@/views/Settings/Users.vue')
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
