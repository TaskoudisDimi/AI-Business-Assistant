<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'

const props = withDefaults(defineProps<{ title: string; subtitle?: string; width?: number }>(), { width: 520 })
const emit = defineEmits<{ (e: 'close'): void }>()

const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') emit('close') }
onMounted(() => document.addEventListener('keydown', onKey))
onBeforeUnmount(() => document.removeEventListener('keydown', onKey))
</script>

<template>
  <Teleport to="body">
    <div class="overlay" @mousedown.self="emit('close')">
      <div class="modal" role="dialog" aria-modal="true" :aria-label="props.title" :style="{ maxWidth: `${props.width}px` }">
        <header class="head">
          <div>
            <h2>{{ props.title }}</h2>
            <p v-if="props.subtitle" class="sub">{{ props.subtitle }}</p>
          </div>
          <button class="ui-icon-btn" aria-label="Close" @click="emit('close')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </header>
        <div class="body"><slot /></div>
        <footer v-if="$slots.footer" class="foot"><slot name="footer" /></footer>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.overlay {
  position: fixed; inset: 0; z-index: 100;
  background: var(--overlay);
  display: flex; align-items: flex-start; justify-content: center;
  padding: 6vh 16px 16px; overflow-y: auto;
  animation: fade .12s ease-out;
}
.modal {
  width: 100%;
  background: var(--bg-card); color: var(--text);
  border: 1px solid var(--border); border-radius: var(--r-xl);
  box-shadow: var(--shadow-lg);
  animation: rise .16s ease-out;
}
.head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; padding: 1.1rem 1.25rem .6rem; }
h2 { font-size: 1.05rem; font-weight: 620; letter-spacing: -.01em; }
.sub { margin-top: .2rem; font-size: .85rem; color: var(--text-muted); }
.body { padding: .5rem 1.25rem 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
.foot { display: flex; justify-content: flex-end; gap: .5rem; padding: .9rem 1.25rem; border-top: 1px solid var(--border-light); }
@keyframes fade { from { opacity: 0 } }
@keyframes rise { from { opacity: 0; transform: translateY(6px) } }
</style>
