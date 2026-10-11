import { defineStore } from 'pinia'
import { api } from '@/services/api'
import type { Router } from 'vue-router'

export interface User {
  id: string
  email: string
  full_name: string
  [key: string]: any
}

export interface Business {
  id: string
  name: string
  industry?: string
  owner_id: string
  created_at: string
}

interface AuthResponse {
  user: User
  businesses: Business[]
  memberships: { business_id: string; role: string }[]
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user:       null as User | null,
    business:   null as Business | null,
    loading:    true,
    error:      null as string | null,
  }),

  getters: {
    isAuthenticated: (state): boolean => !!state.user,
    currentBusiness: (state): Business | null => state.business,
  },

  actions: {
    async initialize(): Promise<void> {
      this.loading = true
      try {
        await this.fetchUser()
      } finally {
        this.loading = false
      }
    },

    async fetchUser(): Promise<void> {
      try {
        const { data } = await api.get<AuthResponse>('/auth/me')
        this.user     = data.user
        this.business = data.businesses?.[0] ?? null
      } catch {
        this.resetAuth()
      }
    },

    async login(email: string, password: string): Promise<boolean> {
      this.loading = true
      this.error   = null
      try {
        await api.post('/auth/login', { email, password })
        await this.fetchUser()
        return true
      } catch (err: unknown) {
        const e = err as { response?: { data?: { detail?: string } } }
        this.error = e.response?.data?.detail ?? 'Login failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async logout(router?: Router): Promise<void> {
      try { await api.post('/auth/logout') } catch { /* ignore */ }
      finally {
        this.resetAuth()
        if (router) router.push('/login')
      }
    },

    resetAuth(): void {
      this.$reset()
    },
  },
})
