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
      { path: "settings", component: () => import("@/views/Settings.vue") }
    ]
  },

  { path: "/", redirect: "/dashboard" }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.user) {
    return "/login"
  }
})

export default router