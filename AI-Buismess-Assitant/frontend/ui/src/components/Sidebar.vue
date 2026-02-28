<script setup lang="ts">
import { useRoute } from "vue-router"

const route = useRoute()

const menu = [
  { name: "Dashboard", path: "/dashboard" },
  { name: "Sales Forecast", path: "/sales" },
  { name: "Customer Analysis", path: "/customers" },
  { name: "Marketing AI", path: "/marketing" },
  { name: "Datasets", path: "/datasets" },
  { name: "History", path: "/history" },
  { name: "Settings", path: "/settings" }
]
</script>

<template>
  <aside class="sidebar">
    <h2 class="logo">AI Assistant</h2>

    <router-link
      v-for="item in menu"
      :key="item.path"
      :to="item.path"
      class="link"
      :class="{ active: route.path === item.path }"
    >
      {{ item.name }}
    </router-link>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 250px;
  background: #111827;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.logo {
  margin-bottom: 40px;
}

.link {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  text-decoration: none;
  color: #cbd5e1;
}

.link.active {
  background: #4f46e5;
  color: white;
}
</style>