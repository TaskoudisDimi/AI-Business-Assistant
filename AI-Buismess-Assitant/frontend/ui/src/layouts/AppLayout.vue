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
  <div class="app-wrapper">
    <aside>
      <h2>AI Assistant</h2>
      <nav>
        <router-link to="/dashboard">Dashboard</router-link>
      </nav>
    </aside>

    <div class="content">
      <header>
        <button @click="logout">Logout</button>
      </header>

      <main>
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-wrapper {
  display: flex;
  min-height: 100vh;
  background: #0f172a;
  color: white;
}

aside {
  width: 240px;
  padding: 2rem;
  background: #111827;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

header {
  padding: 1rem;
  border-bottom: 1px solid #1f2937;
  display: flex;
  justify-content: flex-end;
}

main {
  padding: 2rem;
}
</style>