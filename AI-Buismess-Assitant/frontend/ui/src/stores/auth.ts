import { defineStore } from 'pinia'
import { api } from '@/services/api'
import type { Router } from 'vue-router'

// ====================
// Types
// ====================
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

export interface Membership {
  business_id: string
  role: 'owner' | 'admin' | 'member'
}

interface AuthResponse {
  user: User
  businesses: Business[]
  memberships: Membership[]
}


// ====================
// Store
// ====================
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    businesses: [] as Business[],
    memberships: [] as Membership[],

    currentBusinessId: null as string | null,
    loading: true,
    error: null as string | null,
  }),

  persist: [
    {
      key: 'ai-business-assistant-auth',
      storage: localStorage,
      pick: ['currentBusinessId'],
    },
  ],

  getters: {
    isAuthenticated: (state): boolean => !!state.user,

    currentBusiness: (state): Business | null => {
      if (!state.currentBusinessId) return null
      return state.businesses.find(b => b.id === state.currentBusinessId) ?? null
    },

    currentMembership: (state): Membership | null => {
      if (!state.currentBusinessId) return null
      return (
        state.memberships.find(m => m.business_id === state.currentBusinessId) ?? null
      )
    },

    hasBusinesses: (state): boolean => state.businesses.length > 0,

    isOwner: (state): boolean => {
      const membership = state.memberships.find(
        m => m.business_id === state.currentBusinessId
      )
      return membership?.role === 'owner'
    },
  },

  actions: {
    // ====================
    // Core
    // ====================
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

        this.user = data.user
        this.businesses = data.businesses ?? []
        this.memberships = data.memberships ?? []

        this.resolveCurrentBusiness()
      } catch (error) {
        this.resetAuth()
      }
    },

    resolveCurrentBusiness(): void {
      if (!this.businesses.length) {
        this.currentBusinessId = null
        return
      }

      // try persisted
      if (this.currentBusinessId) {
        const exists = this.businesses.some(b => b.id === this.currentBusinessId)
        if (exists) return
      }

      const first = this.businesses[0]
      if (!first) return

      this.currentBusinessId = first.id 
    },

    setCurrentBusiness(businessId: string): void {
      const exists = this.businesses.some(b => b.id === businessId)
      if (!exists) return

      this.currentBusinessId = businessId
    },

    // ====================
    // Auth
    // ====================
    async login(email: string, password: string): Promise<boolean> {
      this.loading = true
      this.error = null

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
      try {
        await api.post('/auth/logout')
      } catch (_) {
      } finally {
        this.resetAuth()
        if (router) router.push('/login')
      }
    },

    // ====================
    // Utils
    // ====================
    resetAuth(): void {
      this.$reset()
    },
  },
})
