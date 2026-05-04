import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login',    component: () => import('@/views/Auth/Login.vue') },
  { path: '/register', component: () => import('@/views/Auth/Register.vue') },

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
      { path: 'onboarding', component: () => import('@/views/CreateFirstBusiness.vue') },
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

  const isAuthPage = to.path === '/login' || to.path === '/register'

  if (to.meta.requiresAuth && !auth.isAuthenticated) return '/login'

  if (to.meta.requiresAuth && auth.isAuthenticated && !auth.hasBusinesses && to.path !== '/onboarding')
    return '/onboarding'

  if (isAuthPage && auth.isAuthenticated) return '/dashboard'
})

export default router
