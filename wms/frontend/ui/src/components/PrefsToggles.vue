<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocale } from '@/i18n'
import { useTheme } from '@/composables/useTheme'

const { t, locale } = useI18n()
const { theme, cycleTheme } = useTheme()

const toggleLocale = () => setLocale(locale.value === 'el' ? 'en' : 'el')
const themeLabel = computed(() => t(`prefs.theme.${theme.value}`))
</script>

<template>
  <div class="prefs">
    <button class="pref" :title="themeLabel" :aria-label="themeLabel" @click="cycleTheme">
      <!-- system -->
      <svg v-if="theme === 'system'" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>
      <!-- light -->
      <svg v-else-if="theme === 'light'" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      <!-- dark -->
      <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>
    </button>
    <button class="pref pref--text" :title="t('prefs.language')" @click="toggleLocale">
      {{ locale === 'el' ? 'EN' : 'ΕΛ' }}
    </button>
  </div>
</template>

<style scoped>
.prefs { display: flex; gap: .25rem; }
.pref {
  height: 32px; min-width: 32px; padding: 0 .45rem;
  display: grid; place-items: center;
  border-radius: var(--r);
  background: transparent; color: var(--text-sub);
  cursor: pointer;
  transition: background .12s, color .12s;
}
.pref:hover { background: var(--bg-hover); color: var(--text); }
.pref--text { font-size: .78rem; font-weight: 600; }
</style>
