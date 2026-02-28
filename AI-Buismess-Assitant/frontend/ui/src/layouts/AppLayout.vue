<script setup lang="ts">
import Sidebar from "@/components/Sidebar.vue"
import Topbar from "@/components/Topbar.vue"

</script>

<template>
  <div class="app-wrapper">
    <Sidebar />
    <topbar />
    <div class="content">
      <main>
        <router-view />
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