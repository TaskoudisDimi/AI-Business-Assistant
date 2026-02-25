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

const auth = useAuthStore()
const router = useRouter()


const submit = async () => {
  error.value = ""

  if (full_name.value.length < 6) {
    error.value = "Full name must be at least 6 characters."
    return
  }

  if (password.value.length < 6) {
    error.value = "Password must be at least 6 characters."
    return
  }

  try {
    loading.value = true
    await auth.register(email.value, password.value, full_name.value)
    router.push("/login")
  } catch (err: any) {
    error.value = err.response?.data?.detail || "Registration failed"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout>
    <h2>Create Account</h2>
    <p class="subtitle">Start using your AI Business Assistant</p>

    <input v-model="full_name" placeholder="Full Name" />
    <input v-model="email" placeholder="Email" />
    <input v-model="password" type="password" placeholder="Password" />

    <button :disabled="loading" @click="submit">
      {{ loading ? "Creating..." : "Register" }}
    </button>

    <p v-if="error" class="error">{{ error }}</p>

    <router-link to="/login" class="switch">
      Already have an account? Login
    </router-link>
  </AuthLayout>
</template>