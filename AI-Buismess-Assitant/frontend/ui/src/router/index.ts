import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "@/stores/auth"

import LoginView from "@/views/LoginView.vue"
import RegisterView from "@/views/RegisterView.vue"
import DashboardView from "@/views/DashboardView.vue"

const routes = [
  { path: "/login", component: LoginView },
  { path: "/register", component: RegisterView },
  {
    path: "/dashboard",
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  { path: "/", redirect: "/login" }
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