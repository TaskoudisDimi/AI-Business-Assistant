<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore, apiErrorMessage } from '@/stores/auth'
import AuthShell from '@/components/auth/AuthShell.vue'
import PasswordInput from '@/components/auth/PasswordInput.vue'

const MIN_PASSWORD = 8

const { t } = useI18n()
const auth   = useAuthStore()
const router = useRouter()

/* Supabase sends the user here in one of two shapes:
   - default email template: #access_token=…&type=recovery   (or #error=…)
   - custom template:        ?token_hash=…&type=recovery
   Read once and strip it from the address bar so the token doesn't linger in history. */
const hash  = new URLSearchParams(window.location.hash.slice(1))
const query = new URLSearchParams(window.location.search)
const link = {
  access_token: hash.get('access_token') ?? undefined,
  token_hash:   query.get('token_hash') ?? undefined,
}
const hasToken  = !!(link.access_token || link.token_hash)
if (window.location.hash || window.location.search) window.history.replaceState(null, '', window.location.pathname)

const password = ref('')
const confirm  = ref('')
const loading  = ref(false)
const error    = ref('')
const done     = ref(false)

const mismatch = computed(() => confirm.value.length > 0 && confirm.value !== password.value)

const submit = async () => {
  error.value = ''
  if (password.value.length < MIN_PASSWORD) { error.value = t('auth.passwordTooShort', { n: MIN_PASSWORD }); return }
  if (password.value !== confirm.value) { error.value = t('auth.reset.mismatch'); return }

  loading.value = true
  try {
    await auth.resetPassword(password.value, link)
    done.value = true
    // token_hash flow signs the user in; implicit flow doesn't
    await auth.fetchUser()
  } catch (e) {
    error.value = apiErrorMessage(e) || t('common.error')
  } finally {
    loading.value = false
  }
}

const next = () => router.push(auth.isAuthenticated ? '/dashboard' : '/login')
</script>

<template>
  <AuthShell v-if="!hasToken" :title="t('auth.reset.invalidTitle')" :subtitle="t('auth.reset.invalidSub')">
    <router-link to="/forgot-password" class="ui-btn ui-btn--primary ui-btn--block cta">
      {{ t('auth.reset.requestNew') }}
    </router-link>
    <template #footer>
      <router-link to="/login">← {{ t('auth.backToSignIn') }}</router-link>
    </template>
  </AuthShell>

  <AuthShell v-else-if="done" :title="t('auth.reset.doneTitle')" :subtitle="t('auth.reset.doneSub')">
    <button class="ui-btn ui-btn--primary ui-btn--block cta" @click="next">
      {{ auth.isAuthenticated ? t('auth.reset.continue') : t('auth.signIn') }}
    </button>
  </AuthShell>

  <AuthShell v-else :title="t('auth.reset.title')" :subtitle="t('auth.reset.subtitle')">
    <form class="form" novalidate @submit.prevent="submit">
      <div class="ui-field">
        <label class="ui-label" for="password">{{ t('auth.reset.newPassword') }}</label>
        <PasswordInput id="password" v-model="password" autocomplete="new-password" />
        <p class="ui-hint">{{ t('auth.passwordRule', { n: MIN_PASSWORD }) }}</p>
      </div>
      <div class="ui-field">
        <label class="ui-label" for="confirm">{{ t('auth.reset.confirm') }}</label>
        <PasswordInput id="confirm" v-model="confirm" autocomplete="new-password" :invalid="mismatch" />
      </div>

      <p v-if="error" class="ui-alert ui-alert--error" role="alert">{{ error }}</p>

      <button class="ui-btn ui-btn--primary ui-btn--block" type="submit" :disabled="loading || !password || !confirm">
        <span v-if="loading" class="ui-spinner" />
        {{ t('auth.reset.save') }}
      </button>
    </form>
  </AuthShell>
</template>

<style scoped>
.form { display: flex; flex-direction: column; gap: 1.1rem; }
.cta { margin-top: 1.75rem; }
</style>
