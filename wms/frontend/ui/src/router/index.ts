import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login',           component: () => import('@/views/Auth/Login.vue'),          meta: { guestOnly: true } },
  { path: '/register',        component: () => import('@/views/Auth/Register.vue'),       meta: { guestOnly: true } },
  { path: '/forgot-password', component: () => import('@/views/Auth/ForgotPassword.vue'), meta: { guestOnly: true } },
  // Reachable while signed in too: the recovery link may be opened in a browser with an active session
  { path: '/reset-password',  component: () => import('@/views/Auth/ResetPassword.vue') },

  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '',           redirect: 'dashboard' },
      { path: 'dashboard',  component: () => import('@/views/Dashboard.vue') },
      { path: 'sales',      component: () => import('@/views/SalesForecast.vue') },
      { path: 'customers',  component: () => import('@/views/CustomerAnalysis.vue') },
      { path: 'datasets',   component: () => import('@/views/Datasets.vue') },
      { path: 'settings',   component: () => import('@/views/Settings.vue') },
      { path: 'inventory',  component: () => import('@/views/wms/Inventory.vue') },
      { path: 'products',   component: () => import('@/views/wms/Products.vue') },
      { path: 'orders',     component: () => import('@/views/wms/Orders.vue') },
    ],
  },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (auth.loading) await auth.initialize()

  if (to.meta.requiresAuth && !auth.isAuthenticated) return '/login'
  if (to.meta.guestOnly && auth.isAuthenticated) return '/dashboard'
})

export default router
