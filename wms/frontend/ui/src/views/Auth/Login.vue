<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { setLocale } from '@/i18n'

const { t, locale } = useI18n()
const toggleLocale = () => setLocale(locale.value === 'el' ? 'en' : 'el')
const auth   = useAuthStore()
const router = useRouter()

const email    = ref('')
const password = ref('')
const loading  = ref(false)
const error    = ref('')
const showPass = ref(false)

const submit = async () => {
  error.value = ''
  if (password.value.length < 6) { error.value = t('auth.minPassword'); return }
  loading.value = true
  try {
    const ok = await auth.login(email.value, password.value)
    if (ok) router.push('/dashboard')
    else error.value = auth.error || t('auth.wrongCredentials')
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('auth.loginFailed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-root">
    <div class="bg-grid" />

    <button class="lang-btn" @click="toggleLocale">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
      </svg>
      {{ locale === 'el' ? 'EN' : 'EL' }}
    </button>

    <div class="auth-panel">
      <div class="brand">
        <div class="brand-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        <span class="brand-name">AI Assistant</span>
      </div>

      <h1 class="auth-title">{{ t('auth.welcomeBack') }}</h1>
      <p class="auth-sub">{{ t('auth.platformSignIn') }}</p>

      <div class="form">
        <div class="field">
          <label>{{ t('auth.email') }}</label>
          <input v-model="email" type="email" placeholder="name@company.com" @keydown.enter="submit" />
        </div>

        <div class="field">
          <label>{{ t('auth.password') }}</label>
          <div class="input-wrap">
            <input v-model="password" :type="showPass ? 'text' : 'password'" placeholder="••••••••" @keydown.enter="submit" />
            <button class="toggle-pass" @click="showPass = !showPass" tabindex="-1">
              <svg v-if="!showPass" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </button>
          </div>
        </div>

        <Transition name="err">
          <p v-if="error" class="error-msg">{{ error }}</p>
        </Transition>

        <button class="btn-submit" :disabled="loading" @click="submit">
          <span v-if="loading" class="spinner" />
          {{ loading ? t('auth.signingIn') : t('auth.signIn') }}
        </button>
      </div>

      <p class="switch-link">
        {{ t('auth.noAccount') }}
        <router-link to="/register">{{ t('auth.signUp') }}</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-root {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  padding: 1rem;
  position: relative;
  overflow: hidden;
}

.lang-btn {
  position: absolute;
  top: 1.25rem; right: 1.25rem;
  z-index: 10;
  display: flex; align-items: center; gap: .35rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r);
  color: var(--text-muted);
  font-size: .72rem; font-weight: 600;
  padding: .32rem .65rem;
  cursor: pointer; letter-spacing: .04em;
  transition: border-color .15s, color .15s;
}
.lang-btn:hover { border-color: var(--border-mid); color: var(--teal); }

.bg-grid {
  position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(62, 207, 191, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(62, 207, 191, 0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%);
}

.auth-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-xl);
  padding: 2.5rem;
  width: 100%;
  max-width: 400px;
  box-shadow: var(--shadow-lg);
  position: relative;
  z-index: 1;
}

.brand { display: flex; align-items: center; gap: .65rem; margin-bottom: 2rem; }
.brand-icon {
  width: 38px; height: 38px;
  background: linear-gradient(135deg, var(--teal-dark), #0a3a3a);
  border: 1px solid var(--border-mid);
  border-radius: var(--r);
  display: flex; align-items: center; justify-content: center;
  color: var(--teal);
}
.brand-name { font-size: .92rem; font-weight: 700; color: var(--text); letter-spacing: -.02em; }

.auth-title { font-size: 1.5rem; font-weight: 700; color: var(--text); margin: 0; letter-spacing: -.03em; }
.auth-sub   { font-size: .8rem; color: var(--text-muted); margin: .3rem 0 2rem; }

.form { display: flex; flex-direction: column; gap: 1.1rem; }
.field { display: flex; flex-direction: column; gap: .4rem; }

label {
  font-size: .68rem; font-weight: 600;
  color: var(--text-muted);
  letter-spacing: .07em; text-transform: uppercase;
}

input {
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--r);
  color: var(--text);
  padding: .7rem .95rem;
  font-size: .85rem;
  outline: none; width: 100%; box-sizing: border-box;
  transition: border-color .15s, box-shadow .15s;
}
input:focus { border-color: var(--teal-dark); box-shadow: 0 0 0 3px var(--teal-glow); }
input::placeholder { color: var(--text-muted); opacity: .5; }

.input-wrap { position: relative; }
.input-wrap input { padding-right: 2.8rem; }
.toggle-pass {
  position: absolute; right: .8rem; top: 50%; transform: translateY(-50%);
  background: transparent; border: none; color: var(--text-muted); cursor: pointer;
  transition: color .15s; padding: 0;
}
.toggle-pass:hover { color: var(--teal); }

.error-msg {
  font-size: .78rem; color: var(--red);
  background: var(--red-bg); border: 1px solid rgba(224,85,85,.3);
  border-radius: var(--r); padding: .55rem .8rem; margin: 0;
}

.btn-submit {
  display: flex; align-items: center; justify-content: center; gap: .5rem;
  background: var(--teal);
  border: none;
  color: #0a0a0a;
  border-radius: var(--r); padding: .75rem;
  font-size: .88rem; font-weight: 600;
  cursor: pointer; transition: opacity .15s;
}
.btn-submit:hover:not(:disabled) { opacity: .85; }
.btn-submit:disabled { opacity: .35; cursor: not-allowed; }

.switch-link {
  text-align: center; margin-top: 1.5rem;
  font-size: .8rem; color: var(--text-muted);
}
.switch-link a { color: var(--teal); text-decoration: none; font-weight: 600; }
.switch-link a:hover { color: var(--teal-dim); }

.spinner {
  width: 13px; height: 13px; border-radius: 50%;
  border: 2px solid transparent; border-top-color: currentColor;
  animation: spin .6s linear infinite; display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

.err-enter-active { transition: all .2s ease; }
.err-leave-active { transition: all .15s ease; }
.err-enter-from   { opacity: 0; transform: translateY(-4px); }
.err-leave-to     { opacity: 0; }
</style>
