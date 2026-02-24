<script setup lang="ts">
import { useAuthStore } from "@/stores/auth"
import { useRouter } from "vue-router"

const auth = useAuthStore()
const router = useRouter()

const logout = async () => {
  await auth.logout()
  router.push("/login")
}
</script>

<template>
  <div class="dashboard">
    <header>
      <h1>AI Business Assistant</h1>
      <button @click="logout">Logout</button>
    </header>

    <main>
      <h2>Dashboard</h2>
      <p>Your AI analytics will appear here.</p>
    </main>
  </div>
</template>