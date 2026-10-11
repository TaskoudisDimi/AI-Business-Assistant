<script setup lang="ts">
defineProps<{
  title: string
  value: string
}>()
</script>

<template>
  <div class="card">
    <p class="title">{{ title }}</p>
    <h2>{{ value }}</h2>
  </div>
</template>

<style scoped>
.card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.title {
  color: #777;
  margin-bottom: 8px;
}
</style>