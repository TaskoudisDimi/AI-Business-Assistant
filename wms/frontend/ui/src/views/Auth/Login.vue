<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import AuthShell from '@/components/auth/AuthShell.vue'
import PasswordInput from '@/components/auth/PasswordInput.vue'

const { t } = useI18n()
const auth   = useAuthStore()
const router = useRouter()

const email    = ref('')
const password = ref('')
const loading  = ref(false)
const error    = ref('')

const submit = async () => {
  error.value = ''
  loading.value = true
  try {
    if (await auth.login(email.value.trim(), password.value)) router.push('/dashboard')
    else error.value = t('auth.wrongCredentials')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthShell :title="t('auth.welcomeBack')" :subtitle="t('auth.platformSignIn')">
    <form class="form" novalidate @submit.prevent="submit">
      <div class="ui-field">
        <label class="ui-label" for="email">{{ t('auth.email') }}</label>
        <input id="email" v-model="email" class="ui-input" type="email" autocomplete="email"
          placeholder="name@company.com" required autofocus />
      </div>

      <div class="ui-field">
        <label class="ui-label" for="password">
          {{ t('auth.password') }}
          <router-link to="/forgot-password">{{ t('auth.forgotPassword') }}</router-link>
        </label>
        <PasswordInput id="password" v-model="password" autocomplete="current-password" :invalid="!!error" />
      </div>

      <p v-if="error" class="ui-alert ui-alert--error" role="alert">{{ error }}</p>

      <button class="ui-btn ui-btn--primary ui-btn--block" type="submit" :disabled="loading || !email || !password">
        <span v-if="loading" class="ui-spinner" />
        {{ loading ? t('auth.signingIn') : t('auth.signIn') }}
      </button>
    </form>

    <template #footer>
      {{ t('auth.noAccount') }} <router-link to="/register">{{ t('auth.signUp') }}</router-link>
    </template>
  </AuthShell>
</template>

<style scoped>
.form { display: flex; flex-direction: column; gap: 1.1rem; }
</style>
