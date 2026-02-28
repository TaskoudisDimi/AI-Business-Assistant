<script setup lang="ts">
import { ref } from "vue"
import { useAuthStore } from "@/stores/auth"
import { useRouter } from "vue-router"
import AuthLayout from "@/layouts/AuthLayout.vue"

const full_name = ref("")
const email = ref("")
const password = ref("")
const loading = ref(false)
const error = ref("")
const successMessage = ref("")  

const auth = useAuthStore()
const router = useRouter()

const submit = async () => {
  error.value = ""
  successMessage.value = ""

  if (full_name.value.length < 6) {
    error.value = "Το όνομα πρέπει να έχει τουλάχιστον 6 χαρακτήρες."
    return
  }

  if (password.value.length < 6) {
    error.value = "Ο κωδικός πρέπει να έχει τουλάχιστον 6 χαρακτήρες."
    return
  }

  try {
    loading.value = true
    const success = await auth.register(email.value, password.value, full_name.value)
    if (success) {
      successMessage.value = "Η εγγραφή ολοκληρώθηκε! Ελέγξτε το email σας (και spam) για να επιβεβαιώσετε τον λογαριασμό."      
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || "Αποτυχία εγγραφής"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout>
    <h2 class="text-3xl font-bold text-center mb-6">Δημιουργία Λογαριασμού</h2>
    <p class="subtitle text-center mb-8">Ξεκινήστε με τον AI Business Assistant σας</p>

    <form @submit.prevent="submit" class="space-y-5">
      <input v-model="full_name" placeholder="Ονοματεπώνυμο" required class="w-full p-3 rounded-lg bg-gray-800 border border-gray-700 text-white" />
      <input v-model="email" type="email" placeholder="Email" required class="w-full p-3 rounded-lg bg-gray-800 border border-gray-700 text-white" />
      <input v-model="password" type="password" placeholder="Κωδικός" required class="w-full p-3 rounded-lg bg-gray-800 border border-gray-700 text-white" />

      <button
        type="submit"
        :disabled="loading"
        class="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition disabled:opacity-50"
      >
        {{ loading ? "Δημιουργία..." : "Εγγραφή" }}
      </button>
    </form>

    <p v-if="error" class="text-red-400 text-center mt-4">{{ error }}</p>
    <p v-if="successMessage" class="text-green-400 text-center mt-4 font-medium">{{ successMessage }}</p>

    <div class="text-center mt-6">
      <router-link to="/login" class="text-blue-400 hover:text-blue-300">
        Έχετε ήδη λογαριασμό; Συνδεθείτε
      </router-link>
    </div>
  </AuthLayout>
</template>

<style scoped>
h2 {
  color: white;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

input {
  width: 100%;
  margin-bottom: 1rem;
  padding: 0.8rem;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #1e293b;
  color: white;
}

button {
  width: 100%;
  padding: 0.8rem;
  border-radius: 8px;
  border: none;
  background: #3b82f6;
  color: white;
  cursor: pointer;
}

button:hover {
  background: #2563eb;
}

.error {
  color: #ef4444;
  margin-top: 0.5rem;
}

.switch {
  display: block;
  margin-top: 1rem;
  color: #60a5fa;
}
</style>