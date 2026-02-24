import { defineStore } from "pinia"
import { api } from "@/services/api"

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as null | { id: string }
  }),

  actions: {
    async login(email: string, password: string) {
      await api.post("/auth/login", { email, password })
      this.user = { id: "authenticated" }
    },

    async register(email: string, password: string, full_name: string) {
      await api.post("/auth/register", {
        email,
        password,
        full_name
      })
    },

    async logout() {
      await api.post("/auth/logout")
      this.user = null
    }
  }
})