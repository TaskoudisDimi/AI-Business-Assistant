<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore, apiErrorMessage } from '@/stores/auth'
import { api } from '@/services/api'
import { intlLocale } from '@/i18n/format'

type Provider = 'woocommerce' | 'shopify'
interface Integration { id: string; provider: Provider; secret: string; enabled: boolean; webhook_url: string; last_event_at: string | null }

const { t } = useI18n()
const auth = useAuthStore()
const bid = computed(() => auth.currentBusiness?.id ?? '')
const list = ref<Integration[]>([])
const error = ref('')
const shopifySecret = ref('')
const copied = ref('')

const byProvider = (p: Provider) => list.value.find(i => i.provider === p)

async function load() {
  try { list.value = (await api.get('/integrations', { params: { business_id: bid.value } })).data }
  catch (e) { error.value = apiErrorMessage(e) || t('common.error') }
}
onMounted(load)

async function connect(provider: Provider) {
  error.value = ''
  try {
    await api.post('/integrations', { business_id: bid.value, provider, secret: provider === 'shopify' ? shopifySecret.value : null })
    shopifySecret.value = ''
    await load()
  } catch (e) { error.value = apiErrorMessage(e) || t('common.error') }
}

async function toggle(i: Integration) {
  await api.patch(`/integrations/${i.id}`, { enabled: !i.enabled })
  await load()
}

async function remove(i: Integration) {
  if (!confirm(t('integrations.confirmRemove'))) return
  await api.delete(`/integrations/${i.id}`)
  await load()
}

async function copy(text: string, what: string) {
  try { await navigator.clipboard.writeText(text); copied.value = what; setTimeout(() => (copied.value = ''), 1500) } catch { /* ignore */ }
}
</script>

<template>
  <div class="ui-card">
    <div class="ui-card-head">
      <div>
        <p class="ui-card-title">{{ t('integrations.title') }}</p>
        <p class="ui-card-sub">{{ t('integrations.sub') }}</p>
      </div>
    </div>
    <p v-if="error" class="ui-card-body ui-alert ui-alert--error">{{ error }}</p>

    <section v-for="p in (['woocommerce', 'shopify'] as const)" :key="p" class="ui-card-body provider">
      <div class="p-head">
        <strong>{{ p === 'woocommerce' ? 'WooCommerce' : 'Shopify' }}</strong>
        <template v-if="byProvider(p)">
          <span class="ui-badge" :class="byProvider(p)!.enabled ? 'ui-badge--green' : ''">
            {{ byProvider(p)!.enabled ? t('integrations.active') : t('integrations.paused') }}
          </span>
          <span v-if="byProvider(p)!.last_event_at" class="ui-muted small">
            {{ t('integrations.lastOrder', { when: new Date(byProvider(p)!.last_event_at!).toLocaleString(intlLocale()) }) }}
          </span>
        </template>
      </div>

      <template v-if="byProvider(p)">
        <div class="ui-field">
          <label class="ui-label">{{ t('integrations.url') }}</label>
          <div class="copy-row">
            <input class="ui-input ui-input--sm ui-mono" readonly :value="byProvider(p)!.webhook_url" />
            <button class="ui-btn ui-btn--ghost ui-btn--sm" @click="copy(byProvider(p)!.webhook_url, p + 'url')">{{ copied === p + 'url' ? t('draft.copied') : t('draft.copy') }}</button>
          </div>
        </div>
        <div v-if="p === 'woocommerce'" class="ui-field">
          <label class="ui-label">{{ t('integrations.secret') }}</label>
          <div class="copy-row">
            <input class="ui-input ui-input--sm ui-mono" readonly :value="byProvider(p)!.secret" />
            <button class="ui-btn ui-btn--ghost ui-btn--sm" @click="copy(byProvider(p)!.secret, p + 'secret')">{{ copied === p + 'secret' ? t('draft.copied') : t('draft.copy') }}</button>
          </div>
        </div>
        <p class="ui-hint">{{ t(`integrations.steps.${p}`) }}</p>
        <div class="actions">
          <button class="ui-btn ui-btn--ghost ui-btn--sm" @click="toggle(byProvider(p)!)">{{ byProvider(p)!.enabled ? t('integrations.pause') : t('integrations.resume') }}</button>
          <button class="ui-btn ui-btn--danger ui-btn--sm" @click="remove(byProvider(p)!)">{{ t('integrations.disconnect') }}</button>
        </div>
      </template>

      <template v-else>
        <p class="ui-hint">{{ t(`integrations.about.${p}`) }}</p>
        <div v-if="p === 'shopify'" class="copy-row">
          <input v-model="shopifySecret" class="ui-input ui-input--sm" :placeholder="t('integrations.shopifySecret')" />
          <button class="ui-btn ui-btn--primary ui-btn--sm" :disabled="shopifySecret.length < 8" @click="connect(p)">{{ t('integrations.connect') }}</button>
        </div>
        <div v-else><button class="ui-btn ui-btn--primary ui-btn--sm" @click="connect(p)">{{ t('integrations.connect') }}</button></div>
      </template>
    </section>
    <p class="ui-card-body ui-hint">{{ t('integrations.skuNote') }}</p>
  </div>
</template>

<style scoped>
.provider { display: flex; flex-direction: column; gap: .75rem; border-bottom: 1px solid var(--border-light); }
.p-head { display: flex; align-items: center; gap: .6rem; flex-wrap: wrap; }
.copy-row { display: flex; gap: .5rem; }
.copy-row .ui-input { flex: 1; }
.actions { display: flex; gap: .5rem; }
.small { font-size: .8rem; }
</style>
