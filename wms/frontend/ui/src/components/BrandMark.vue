<script setup lang="ts">
withDefaults(defineProps<{ size?: number; withName?: boolean }>(), { size: 28, withName: true })
</script>

<template>
  <span class="brand">
    <svg :width="size" :height="size" viewBox="0 0 32 32" aria-hidden="true">
      <rect width="32" height="32" rx="8" fill="var(--accent)" />
      <path d="M8 12.5 16 8l8 4.5V23a1 1 0 0 1-1 1h-4v-6h-6v6H9a1 1 0 0 1-1-1z" fill="var(--accent-text)" />
    </svg>
    <span v-if="withName" class="brand-name">WMS</span>
  </span>
</template>

<style scoped>
.brand { display: inline-flex; align-items: center; gap: .55rem; }
.brand svg { flex-shrink: 0; display: block; }
.brand-name { font-weight: 650; font-size: .95rem; letter-spacing: -.01em; color: var(--text); }
</style>
