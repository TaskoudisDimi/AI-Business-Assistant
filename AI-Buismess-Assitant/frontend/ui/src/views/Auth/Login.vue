<script setup lang="ts">
import { ref } from "vue"
import { useAuthStore } from "@/stores/auth"
import { useRouter } from "vue-router"
import AuthLayout from "@/layouts/AuthLayout.vue"

const email = ref("")
const password = ref("")
const loading = ref(false)
const error = ref("")

const auth = useAuthStore()
const router = useRouter()

const submit = async () => {
  error.value = ""

  if (password.value.length < 6) {
    error.value = "Password must be at least 6 characters."
    return
  }

  try {
    loading.value = true
    const success = await auth.login(email.value, password.value)
    if (success) {
      router.push('/dashboard')
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || "Invalid credentials"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout>
    <p class="subtitle">Login to your AI Business Assistant</p>

    <input v-model="email" placeholder="Email" />
    <input v-model="password" type="password" placeholder="Password" />

    <button :disabled="loading" @click="submit">
      {{ loading ? "Logging in..." : "Login" }}
    </button>

    <p v-if="error" class="error">{{ error }}</p>

    <router-link to="/register" class="switch">
      Don't have an account? Register
    </router-link>
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