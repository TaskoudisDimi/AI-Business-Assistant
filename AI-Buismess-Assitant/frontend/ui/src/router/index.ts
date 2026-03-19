import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "@/stores/auth"

import LoginView from "@/views/Auth/Login.vue"
import RegisterView from "@/views/Auth/Register.vue"
import AppLayout from "@/layouts/AppLayout.vue"

const routes = [
  { path: "/login", component: LoginView },
  { path: "/register", component: RegisterView },

  {
    path: "/",
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      { path: "dashboard", component: () => import("@/views/Dashboard.vue") },
      { path: "sales", component: () => import("@/views/SalesForecast.vue") },
      { path: "customers", component: () => import("@/views/CustomerAnalysis.vue") },
      { path: "marketing", component: () => import("@/views/MarketingAI.vue") },
      { path: "datasets", component: () => import("@/views/Datasets.vue") },
      { path: "history", component: () => import("@/views/History.vue") },
      { path: "settings", component: () => import("@/views/Settings.vue") },
      {
        path: '/onboarding',
        component: () => import('@/views/CreateFirstBusiness.vue'),
        meta: { requiresAuth: true }
      },
    ]
  },

  { path: "/", redirect: "/dashboard" }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})
// router/index.ts
router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Περίμενε το initialization αν είναι σε εξέλιξη
  if (auth.loading) {
    await auth.initialize()
  }

  // Τώρα είμαστε σίγουροι ότι έχουμε φορτώσει τον user (ή όχι)
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return '/login'
  }

  // Αν authenticated αλλά ΔΕΝ έχει business → onboarding
  if (to.meta.requiresAuth && auth.isAuthenticated && !auth.hasBusinesses && to.path !== '/onboarding') {
    return '/onboarding'
  }

  // Αν πάει login/register ενώ είναι συνδεδεμένος → dashboard
  if ((to.path === '/login' || to.path === '/register') && auth.isAuthenticated) {
    return '/dashboard'
  }
})

export default router