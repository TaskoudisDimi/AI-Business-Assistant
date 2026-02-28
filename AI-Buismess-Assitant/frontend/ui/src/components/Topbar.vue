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
  <header class="topbar">
    <div>
      <button @click="logout">Logout</button>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  height: 70px;
  background: #111827;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 32px;
  border-bottom: 1px solid #1f2937;
}
</style>