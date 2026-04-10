<!-- ════════════════════════════════════════════════════════════════
     FILE: src/layouts/AppLayout.vue
════════════════════════════════════════════════════════════════ -->
<script setup lang="ts">
import Sidebar from "@/components/Sidebar.vue"
import Topbar  from "@/components/Topbar.vue"
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
  background: #080d16;
  color: #c8d6e8;
}
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;   /* prevent flex overflow */
}
.page {
  flex: 1;
  overflow-y: auto;
}
@media (max-width: 768px) {
  .layout { flex-direction: column; }
}
</style>