<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseModal from '@/components/ui/BaseModal.vue'
import { api } from '@/services/api'
import { apiErrorMessage } from '@/stores/auth'

const props = defineProps<{ businessId: string; customer: string }>()
const emit = defineEmits<{ (e: 'close'): void }>()
const { t, locale } = useI18n()

const channel = ref<'email' | 'sms'>('email')
const offer = ref('')
const text = ref('')
const loading = ref(false)
const error = ref('')
const copied = ref(false)

async function generate() {
  loading.value = true; error.value = ''; copied.value = false
  try {
    const { data } = await api.post('/ai/draft-message', {
      business_id: props.businessId, customer_name: props.customer, language: locale.value,
      channel: channel.value, offer: offer.value || null,
    }, { timeout: 120_000 })
    text.value = data.message
  } catch (e) {
    error.value = apiErrorMessage(e) || t('common.error')
  } finally { loading.value = false }
}

async function copy() {
  try { await navigator.clipboard.writeText(text.value); copied.value = true } catch { /* ignore */ }
}

onMounted(generate)
</script>

<template>
  <BaseModal :title="t('draft.title')" :subtitle="customer" :width="600" @close="emit('close')">
    <div class="opts">
      <div class="seg">
        <button v-for="c in (['email', 'sms'] as const)" :key="c" :class="{ on: channel === c }" @click="channel = c">{{ t(`draft.${c}`) }}</button>
      </div>
      <input v-model="offer" class="ui-input ui-input--sm" :placeholder="t('draft.offer')" />
      <button class="ui-btn ui-btn--ghost ui-btn--sm" :disabled="loading" @click="generate">{{ t('draft.regenerate') }}</button>
    </div>
    <div v-if="loading" class="ui-muted loading"><span class="ui-spinner" /> {{ t('draft.writing') }}</div>
    <p v-else-if="error" class="ui-alert ui-alert--error">{{ error }}</p>
    <textarea v-else v-model="text" class="ui-textarea" rows="9" />
    <p class="ui-hint">{{ t('draft.hint') }}</p>
    <template #footer>
      <button class="ui-btn ui-btn--ghost" @click="emit('close')">{{ t('common.close') }}</button>
      <button class="ui-btn ui-btn--primary" :disabled="!text || loading" @click="copy">{{ copied ? t('draft.copied') : t('draft.copy') }}</button>
    </template>
  </BaseModal>
</template>

<style scoped>
.opts { display: flex; gap: .5rem; flex-wrap: wrap; align-items: center; }
.opts .ui-input { flex: 1; min-width: 180px; }
.seg { display: inline-flex; border: 1px solid var(--border-mid); border-radius: var(--r); overflow: hidden; }
.seg button { background: none; padding: 0 .75rem; height: 32px; font-size: .83rem; color: var(--text-sub); cursor: pointer; }
.seg button.on { background: var(--accent-soft); color: var(--accent); font-weight: 550; }
.loading { display: flex; gap: .5rem; align-items: center; min-height: 120px; }
</style>
