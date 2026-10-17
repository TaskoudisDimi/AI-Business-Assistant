<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore, apiErrorMessage } from '@/stores/auth'
import { api } from '@/services/api'

const { t } = useI18n()
const auth = useAuthStore()
const bid = computed(() => auth.currentBusiness?.id ?? '')
const enabled = ref(auth.currentBusiness?.alert_email_enabled ?? true)
const preview = ref<{ reorder: unknown[]; expiring: unknown[]; anomalies: unknown[]; smtp_configured: boolean } | null>(null)
const msg = ref<{ type: 'error' | 'success'; text: string } | null>(null)
const sending = ref(false)

onMounted(async () => {
  preview.value = (await api.get('/alerts/preview', { params: { business_id: bid.value } })).data
})

async function toggle() {
  await api.patch(`/businesses/${bid.value}`, { alert_email_enabled: enabled.value })
  if (auth.currentBusiness) auth.currentBusiness.alert_email_enabled = enabled.value
}

async function sendTest() {
  sending.value = true; msg.value = null
  try {
    const { data } = await api.post('/alerts/test', null, { params: { business_id: bid.value } })
    msg.value = { type: 'success', text: t('alerts.sent', { email: data.sent_to }) }
  } catch (e) {
    msg.value = { type: 'error', text: apiErrorMessage(e) || t('common.error') }
  } finally { sending.value = false }
}
</script>

<template>
  <div class="ui-card">
    <div class="ui-card-head">
      <div>
        <p class="ui-card-title">{{ t('alerts.title') }}</p>
        <p class="ui-card-sub">{{ t('alerts.sub') }}</p>
      </div>
    </div>
    <div class="ui-card-body body">
      <label class="ui-check"><input v-model="enabled" type="checkbox" :disabled="!auth.isAdmin" @change="toggle" /> {{ t('alerts.enable') }}</label>
      <p v-if="preview && !preview.smtp_configured" class="ui-alert ui-alert--warn">{{ t('alerts.noSmtp') }}</p>
      <div v-if="preview" class="today">
        <p class="ui-label">{{ t('alerts.today') }}</p>
        <ul>
          <li>{{ t('alerts.reorder', { n: preview.reorder.length }) }}</li>
          <li>{{ t('alerts.expiring', { n: preview.expiring.length }) }}</li>
          <li>{{ t('alerts.anomalies', { n: preview.anomalies.length }) }}</li>
        </ul>
      </div>
      <div v-if="auth.isAdmin">
        <button class="ui-btn ui-btn--ghost ui-btn--sm" :disabled="sending || !preview?.smtp_configured" @click="sendTest">
          <span v-if="sending" class="ui-spinner" />{{ t('alerts.test') }}
        </button>
      </div>
      <p v-if="msg" class="ui-alert" :class="msg.type === 'error' ? 'ui-alert--error' : 'ui-alert--success'">{{ msg.text }}</p>
    </div>
  </div>
</template>

<style scoped>
.body { display: flex; flex-direction: column; gap: .9rem; }
.today ul { margin-top: .4rem; padding-left: 1.1rem; color: var(--text-sub); font-size: .88rem; display: grid; gap: .2rem; }
</style>
