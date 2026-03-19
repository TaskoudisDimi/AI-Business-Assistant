<!-- src/components/CreateFirstBusiness.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { api } from "@/services/api"
const authStore = useAuthStore()
const router = useRouter()

const name = ref('')
const industry = ref('')
const loading = ref(false)
const error = ref<string | null>(null)

const createBusiness = async () => {
  if (!name.value.trim()) {
    error.value = 'Το όνομα είναι υποχρεωτικό'
    return
  }

  loading.value = true
  error.value = null

  try {
    await api.post('/businesses', {
      name: name.value,
      industry: industry.value || null
    })

    // Refresh user data (τώρα θα έχει businesses)
    await authStore.fetchUser()

    // Redirect μετά την επιτυχία
    router.push('/dashboard')
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Αποτυχία δημιουργίας επιχείρησης'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-gray-800 p-8 rounded-xl w-full max-w-md">
      <h2 class="text-2xl font-bold mb-6 text-center">Δημιούργησε την πρώτη σου επιχείρηση</h2>
      
      <p class="text-gray-300 mb-6">
        Για να ξεκινήσεις να χρησιμοποιείς την πλατφόρμα, χρειάζεται να δημιουργήσεις μια επιχείρηση.
      </p>

      <form @submit.prevent="createBusiness">
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Όνομα επιχείρησης *</label>
          <input
            v-model="name"
            type="text"
            class="w-full p-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="π.χ. Η Εταιρεία μου"
            required
          />
        </div>

        <div class="mb-6">
          <label class="block text-sm font-medium mb-2">Κλάδος (προαιρετικό)</label>
          <input
            v-model="industry"
            type="text"
            class="w-full p-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="π.χ. Λιανική, Τεχνολογία, Υπηρεσίες"
          />
        </div>

        <p v-if="error" class="text-red-400 mb-4 text-center">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold disabled:opacity-50"
        >
          {{ loading ? 'Δημιουργία...' : 'Δημιουργία' }}
        </button>
      </form>
    </div>
  </div>
</template>