<script setup lang="ts">
withDefaults(defineProps<{ size?: number; withName?: boolean }>(), { size: 28, withName: true })
</script>

<template>
  <span class="brand">
    <!-- Logo traced from imgs/MainLogo.webp; colors come from --brand-* so it adapts to dark mode -->
    <svg :height="size" :width="size * 0.69" viewBox="112 48 276 404" aria-hidden="true">
      <path d="M116 52H196V160H305V240H116Z" fill="var(--brand-light)" />
      <path d="M116 260H196V347A22 22 0 0 0 240 347H318A101 101 0 0 1 116 347Z" fill="var(--brand-dark)" />
      <circle cx="353" cy="416" r="31" fill="var(--brand-dark)" />
    </svg>
    <span v-if="withName" class="brand-name">WMS</span>
  </span>
</template>

<style scoped>
.brand { display: inline-flex; align-items: center; gap: .6rem; }
.brand svg { flex-shrink: 0; display: block; }
.brand-name { font-weight: 650; font-size: .98rem; letter-spacing: -.01em; color: var(--text); }
</style>
