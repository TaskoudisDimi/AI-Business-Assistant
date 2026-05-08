<script setup lang="ts">
import Sidebar from '@/components/Sidebar.vue'
import Topbar  from '@/components/Topbar.vue'
</script>

<template>
  <div class="layout">
    <Sidebar />
    <div class="main">
      <Topbar />
      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  width: 100%;
  height: 100%;
  background: var(--bg);
  overflow: hidden;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.content {
  flex: 1;
  overflow-y: auto;
}
</style>
