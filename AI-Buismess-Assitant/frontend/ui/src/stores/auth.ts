import { defineStore } from 'pinia'
import { api } from '@/services/api'
import type { Router } from 'vue-router' 

interface User {
  id: string
  email: string
  full_name: string
  [key: string]: any
}
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    loading: true,  
    error: null as string | null,
  }),

  getters: {
    isAuthenticated: (state): boolean => !!state.user,
  },

  actions: {
    async fetchUser(): Promise<void> {
      try {
        const response = await api.get('/auth/me')
        this.user = response.data.user
      } catch (err) {
        this.user = null
      }
    },

    async initialize(): Promise<void> {
      try {
        await this.fetchUser()
      } finally {
        this.loading = false  
      }
    },

    async login(email: string, password: string): Promise<boolean> {
      this.loading = true
      this.error = null

      try {
        await api.post('/auth/login', { email, password })
        await this.fetchUser()
        return true
      } catch (err: any) {
        this.error =
          err.response?.data?.detail ||
          'Αποτυχία σύνδεσης. Ελέγξτε τα στοιχεία σας.'
        return false
      } finally {
        this.loading = false
      }
    },

    async logout(router?: Router): Promise<void> {
      try {
        await api.post('/auth/logout')
      } finally {
        this.user = null
        this.loading = false
        if (router) router.push('/login')
      }
    },
  },
})