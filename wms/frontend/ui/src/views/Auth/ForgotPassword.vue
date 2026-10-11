<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore, apiErrorMessage } from '@/stores/auth'
import AuthShell from '@/components/auth/AuthShell.vue'

const { t } = useI18n()
const auth = useAuthStore()

const email   = ref('')
const loading = ref(false)
const error   = ref('')
const sentTo  = ref('')

const submit = async () => {
  error.value = ''
  loading.value = true
  try {
    await auth.requestPasswordReset(email.value.trim())
    sentTo.value = email.value.trim()
  } catch (e) {
    error.value = apiErrorMessage(e) || t('common.error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthShell v-if="!sentTo" :title="t('auth.forgot.title')" :subtitle="t('auth.forgot.subtitle')">
    <form class="form" novalidate @submit.prevent="submit">
      <div class="ui-field">
        <label class="ui-label" for="email">{{ t('auth.email') }}</label>
        <input id="email" v-model="email" class="ui-input" type="email" autocomplete="email"
          placeholder="name@company.com" required autofocus />
      </div>

      <p v-if="error" class="ui-alert ui-alert--error" role="alert">{{ error }}</p>

      <button class="ui-btn ui-btn--primary ui-btn--block" type="submit" :disabled="loading || !email">
        <span v-if="loading" class="ui-spinner" />
        {{ t('auth.forgot.send') }}
      </button>
    </form>

    <template #footer>
      <router-link to="/login">← {{ t('auth.backToSignIn') }}</router-link>
    </template>
  </AuthShell>

  <AuthShell v-else :title="t('auth.checkInbox')">
    <p class="sent">{{ t('auth.forgot.sent', { email: sentTo }) }}</p>
    <p class="ui-hint">{{ t('auth.checkSpam') }}</p>
    <button class="ui-btn ui-btn--ghost ui-btn--block resend" :disabled="loading" @click="sentTo = ''">
      {{ t('auth.forgot.tryAnother') }}
    </button>
    <template #footer>
      <router-link to="/login">← {{ t('auth.backToSignIn') }}</router-link>
    </template>
  </AuthShell>
</template>

<style scoped>
.form { display: flex; flex-direction: column; gap: 1.1rem; }
.sent { margin: .4rem 0 .75rem; color: var(--text-sub); font-size: .92rem; }
.resend { margin-top: 1.5rem; }
</style>
