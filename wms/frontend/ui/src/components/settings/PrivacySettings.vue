<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '@/services/api'

const { t } = useI18n()
const exporting = ref(false)

async function exportData() {
  exporting.value = true
  try {
    const { data } = await api.get('/user/export', { timeout: 120_000 })
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `wms-export-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(a.href)
  } finally { exporting.value = false }
}
</script>

<template>
  <div class="ui-card">
    <div class="ui-card-head">
      <div>
        <p class="ui-card-title">{{ t('privacy.exportTitle') }}</p>
        <p class="ui-card-sub">{{ t('privacy.exportSub') }}</p>
      </div>
      <button class="ui-btn ui-btn--ghost ui-btn--sm" :disabled="exporting" @click="exportData">
        <span v-if="exporting" class="ui-spinner" />{{ t('privacy.export') }}
      </button>
    </div>
    <div class="ui-card-body links">
      <router-link to="/privacy" target="_blank">{{ t('legal.privacyTitle') }}</router-link>
      <router-link to="/terms" target="_blank">{{ t('legal.termsTitle') }}</router-link>
    </div>
  </div>
</template>

<style scoped>
.links { display: flex; gap: 1.25rem; font-size: .88rem; }
.links a { color: var(--accent); }
</style>
