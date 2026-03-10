<script setup lang="ts">
import { ref } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()
const collapsed = ref(false)

const menu = [
  { name: "Dashboard", path: "/dashboard", icon: "📊" },
  { name: "Sales Forecast", path: "/sales", icon: "📈" },
  { name: "Customer Analysis", path: "/customers", icon: "👥" },
  { name: "Marketing AI", path: "/marketing", icon: "🎯" },
  { name: "Datasets", path: "/datasets", icon: "🗂" },
  { name: "History", path: "/history", icon: "🕓" },
  { name: "Settings", path: "/settings", icon: "⚙️" }
]
</script>

<template>
  <aside :class="['sidebar', { collapsed }]">

    <!-- Top Section -->
    <div class="top">
      <h2 v-if="!collapsed" class="logo">AI Assistant</h2>

      <button class="collapse-btn" @click="collapsed = !collapsed">
        {{ collapsed ? "➡" : "⬅" }}
      </button>
    </div>

    <!-- Menu -->
    <router-link
      v-for="item in menu"
      :key="item.path"
      :to="item.path"
      class="link"
      :class="{ active: route.path === item.path }"
    >
      <span class="icon">{{ item.icon }}</span>
      <span v-if="!collapsed">{{ item.name }}</span>
    </router-link>

  </aside>
</template>

<style scoped>
.sidebar {
  width: 250px;
  background: #111827;
  padding: 20px;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 80px;
}

.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
}

.logo {
  font-size: 18px;
}

.collapse-btn {
  background: none;
  border: none;
  color: #cbd5e1;
  cursor: pointer;
  font-size: 16px;
}

.link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  text-decoration: none;
  color: #cbd5e1;
  transition: background 0.2s;
}

.link:hover {
  background: #1e293b;
}

.link.active {
  background: #4f46e5;
  color: white;
}

.icon {
  font-size: 18px;
}
</style>