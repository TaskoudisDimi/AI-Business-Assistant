<script setup lang="ts">
import Sidebar from "@/components/Sidebar.vue"
import Topbar from "@/components/Topbar.vue"
</script>

<template>
  <div class="layout">
    <Sidebar />

    <div class="main">
      <Topbar />
      <div class="page">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background: #0f172a;
  color: white;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.page {
  padding: 2rem;
  flex: 1;
}

/* Mobile */
@media (max-width: 900px) {
  .layout {
    flex-direction: column;
  }
}
</style>