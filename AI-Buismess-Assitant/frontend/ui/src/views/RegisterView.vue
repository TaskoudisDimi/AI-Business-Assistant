<script setup lang="ts">
import { ref } from "vue"
import { useAuthStore } from "@/stores/auth"
import { useRouter } from "vue-router"

const full_name = ref("")
const email = ref("")
const password = ref("")
const auth = useAuthStore()
const router = useRouter()

const submit = async () => {
  await auth.register(email.value, password.value, full_name.value)
  router.push("/login")
}
</script>

<template>
  <div class="auth-container">
    <h2>Register</h2>
    <input v-model="full_name" placeholder="Full Name" />
    <input v-model="email" placeholder="Email" />
    <input v-model="password" type="password" placeholder="Password" />
    <button @click="submit">Register</button>
  </div>
</template>