// src/stores/auth.ts
import { defineStore } from 'pinia'
import { api } from '@/services/api'  // το axios instance σου
import type { Router } from 'vue-router'  // αν χρειαστείς router μέσα στο store (προαιρετικό)

interface User {
  id: string
  email: string
  full_name: string
  // πρόσθεσε όποια άλλα fields επιστρέφει το /auth/me
  [key: string]: any
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    loading: false,
    error: null as string | null,
  }),

  getters: {
    isAuthenticated: (state): boolean => !!state.user,
    // π.χ. isAdmin: (state) => state.user?.role === 'admin',
  },

  actions: {
    /**
     * Εκτελεί login και φορτώνει τα στοιχεία του χρήστη
     * @returns true αν πέτυχε, false αν απέτυχε
     */
    async login(email: string, password: string): Promise<boolean> {
      this.loading = true
      this.error = null

      try {
        await api.post('/auth/login', { email, password })
        await this.fetchUser()
        return true
      } catch (err: any) {
        this.error = err.response?.data?.detail || 'Αποτυχία σύνδεσης. Ελέγξτε τα στοιχεία σας.'
        console.error('Login error:', err)
        return false
      } finally {
        this.loading = false
      }
    },

    /**
     * Εγγραφή νέου χρήστη
     * @returns true αν πέτυχε η εγγραφή, false αλλιώς
     */
    async register(email: string, password: string, full_name: string): Promise<boolean> {
      this.loading = true
      this.error = null

      try {
        await api.post('/auth/register', { email, password, full_name })
        // Συνήθως μετά register πηγαίνουμε σε /login ή /confirm
        // Δεν κάνουμε auto-login λόγω email confirmation
        return true
      } catch (err: any) {
        this.error = err.response?.data?.detail || 'Αποτυχία εγγραφής. Δοκιμάστε ξανά.'
        console.error('Register error:', err)
        return false
      } finally {
        this.loading = false
      }
    },

    /**
     * Φορτώνει τα στοιχεία του τρέχοντος χρήστη από το /auth/me
     * Χρησιμοποιείται στο app init και μετά από login
     */
    async fetchUser(): Promise<void> {
      // Δεν βάζουμε loading εδώ για να μην κρύβει όλη την οθόνη σε silent checks
      try {
        const response = await api.get('/auth/me')
        this.user = response.data
        this.error = null
      } catch (err) {
        this.user = null
        // Μην βάζεις error εδώ – συνήθως silent fail αν δεν είσαι logged in
      }
    },

    /**
     * Αποσύνδεση χρήστη
     */
    async logout(router?: Router): Promise<void> {
      this.loading = true

      try {
        await api.post('/auth/logout')
      } catch (err) {
        console.warn('Logout request failed, but clearing local state anyway', err)
      } finally {
        this.user = null
        this.error = null
        this.loading = false

        // Αν έχεις router, κάνε redirect
        if (router) {
          router.push('/login')
        }
      }
    },

    /**
     * Αρχικοποίηση κατάστασης auth (καλείται στο main.ts)
     */
    async initialize(): Promise<void> {
      if (!this.user) {
        await this.fetchUser()
      }
    },

    /**
     * Καθαρισμός error μηνύματος (χρήσιμο σε forms)
     */
    clearError() {
      this.error = null
    },
  },
})