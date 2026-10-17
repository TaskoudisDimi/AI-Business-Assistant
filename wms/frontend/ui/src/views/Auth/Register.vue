<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore, apiErrorMessage } from '@/stores/auth'
import AuthShell from '@/components/auth/AuthShell.vue'
import PasswordInput from '@/components/auth/PasswordInput.vue'

const MIN_PASSWORD = 8

const { t } = useI18n()
const auth = useAuthStore()

const fullName = ref('')
const email    = ref('')
const password = ref('')
const loading  = ref(false)
const error    = ref('')
const sentTo   = ref('')       // set once the confirmation email is on its way
const confirmed = ref(false)   // project has email confirmation disabled

const passwordTooShort = computed(() => password.value.length > 0 && password.value.length < MIN_PASSWORD)

const submit = async () => {
  error.value = ''
  if (fullName.value.trim().length < 2) { error.value = t('auth.nameTooShort'); return }
  if (password.value.length < MIN_PASSWORD) { error.value = t('auth.passwordTooShort', { n: MIN_PASSWORD }); return }

  loading.value = true
  try {
    const res = await auth.register(email.value.trim(), password.value, fullName.value.trim())
    confirmed.value = res.confirmed
    sentTo.value = email.value.trim()
  } catch (e) {
    error.value = apiErrorMessage(e) || t('auth.registerFailed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthShell v-if="!sentTo" :title="t('auth.register')" :subtitle="t('auth.startFree')">
    <form class="form" novalidate @submit.prevent="submit">
      <div class="ui-field">
        <label class="ui-label" for="name">{{ t('auth.fullName') }}</label>
        <input id="name" v-model="fullName" class="ui-input" autocomplete="name" required autofocus />
      </div>
      <div class="ui-field">
        <label class="ui-label" for="email">{{ t('auth.email') }}</label>
        <input id="email" v-model="email" class="ui-input" type="email" autocomplete="email"
          placeholder="name@company.com" required />
      </div>
      <div class="ui-field">
        <label class="ui-label" for="password">{{ t('auth.password') }}</label>
        <PasswordInput id="password" v-model="password" autocomplete="new-password" :invalid="passwordTooShort" />
        <p class="ui-hint">{{ t('auth.passwordRule', { n: MIN_PASSWORD }) }}</p>
      </div>

      <p v-if="error" class="ui-alert ui-alert--error" role="alert">{{ error }}</p>

      <button class="ui-btn ui-btn--primary ui-btn--block" type="submit" :disabled="loading || !email || !password || !fullName">
        <span v-if="loading" class="ui-spinner" />
        {{ loading ? t('auth.creatingAccount') : t('auth.signUp') }}
      </button>
      <i18n-t keypath="legal.consent" tag="p" class="ui-hint consent">
        <template #terms><router-link to="/terms" target="_blank">{{ t('legal.termsTitle') }}</router-link></template>
        <template #privacy><router-link to="/privacy" target="_blank">{{ t('legal.privacyTitle') }}</router-link></template>
      </i18n-t>
    </form>

    <template #footer>
      {{ t('auth.hasAccount') }} <router-link to="/login">{{ t('auth.signIn') }}</router-link>
    </template>
  </AuthShell>

  <AuthShell v-else-if="confirmed" :title="t('auth.accountReady')" :subtitle="t('auth.accountReadySub')">
    <router-link to="/login" class="ui-btn ui-btn--primary ui-btn--block cta">{{ t('auth.signIn') }}</router-link>
  </AuthShell>

  <AuthShell v-else :title="t('auth.checkInbox')">
    <p class="sent">{{ t('auth.confirmSent', { email: sentTo }) }}</p>
    <p class="ui-hint">{{ t('auth.checkSpam') }}</p>
    <template #footer>
      <router-link to="/login">← {{ t('auth.backToSignIn') }}</router-link>
    </template>
  </AuthShell>
</template>

<style scoped>
.form { display: flex; flex-direction: column; gap: 1.1rem; }
.cta { margin-top: 1.75rem; }
.consent { text-align: center; }
.consent a { color: var(--text-sub); text-decoration: underline; }
.sent { margin: .4rem 0 .75rem; color: var(--text-sub); font-size: .92rem; }
</style>
