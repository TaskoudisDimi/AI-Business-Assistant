<script setup lang="ts"></script>

<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #0f172a;
}

.auth-card {
  width: 400px;
  padding: 2rem;
  border-radius: 16px;
  background: #0f172a;
  box-shadow: 0 20px 40px rgba(0,0,0,0.4);
  border: 1px solid #1e293b;
}
</style>