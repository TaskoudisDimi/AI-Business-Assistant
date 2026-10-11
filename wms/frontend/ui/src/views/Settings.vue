<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'
import { useI18n } from 'vue-i18n'
import { setLocale } from '@/i18n'

const auth  = useAuthStore()
const { t } = useI18n()

const loading   = ref(false)
const toast     = ref<{ msg: string; type: 'success' | 'error' } | null>(null)
const activeTab = ref<'account' | 'security'>('account')

const showToast = (msg: string, type: 'success' | 'error' = 'success') => {
  toast.value = { msg, type }
  setTimeout(() => (toast.value = null), 3000)
}

/* ── Account ── */
const fullName = ref('')
const username = ref('')
const email    = ref('')
const language = ref('el')

watch(() => auth.user, (u) => {
  if (!u) return
  fullName.value = u.full_name ?? ''
  username.value = u.username  ?? ''
  email.value    = u.email     ?? ''
  language.value = u.language  ?? 'el'
}, { immediate: true })

const saveAccount = async () => {
  loading.value = true
  try {
    await api.patch('/user', { full_name: fullName.value, username: username.value, language: language.value })
    if (auth.user) {
      auth.user.full_name = fullName.value
      auth.user.username  = username.value
      auth.user.language  = language.value
    }
    setLocale(language.value as 'el' | 'en')
    showToast(t('settings.account.saved'))
  } catch { showToast(t('common.error'), 'error') }
  finally  { loading.value = false }
}

const changeEmail = async () => {
  try {
    await api.patch('/user/email', { email: email.value })
    if (auth.user) auth.user.email = email.value
    showToast(t('settings.account.emailUpdated'))
  } catch { showToast(t('common.error'), 'error') }
}

/* ── Security ── */
const newPassword   = ref('')
const confirmPass   = ref('')
const showPass      = ref(false)
const deleteConfirm = ref('')

const passwordsMatch = computed(() => !confirmPass.value || newPassword.value === confirmPass.value)

const changePassword = async () => {
  if (!passwordsMatch.value) return
  try {
    await api.patch('/user/password', { password: newPassword.value })
    newPassword.value = ''
    confirmPass.value = ''
    showToast(t('settings.security.passwordChanged'))
  } catch { showToast(t('common.error'), 'error') }
}

const deleteAccount = async () => {
  if (deleteConfirm.value !== 'DELETE') return
  await api.delete('/user')
  window.location.href = '/login'
}

const initials = computed(() =>
  (auth.user?.full_name ?? 'U').split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
)

const tabs = [
  { key: 'account',  label: t('settings.tabs.account'),  icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>` },
  { key: 'security', label: t('settings.tabs.security'), icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>` },
]
</script>

<template>
  <div class="settings">

    <!-- Toast -->
    <Transition name="toast-slide">
      <div v-if="toast" class="toast" :class="`toast--${toast.type}`">
        <svg v-if="toast.type === 'success'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ toast.msg }}
      </div>
    </Transition>

    <!-- Header -->
    <div class="settings-header">
      <div class="avatar-block">
        <div class="avatar-xl">{{ initials }}</div>
        <div>
          <p class="avatar-name">{{ auth.user?.full_name }}</p>
          <p class="avatar-email">{{ auth.user?.email }}</p>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab-btn"
        :class="{ 'tab-btn--active': activeTab === tab.key }"
        @click="activeTab = tab.key as any"
      >
        <span v-html="tab.icon" />
        {{ tab.label }}
      </button>
    </div>

    <!-- Account Tab -->
    <Transition name="tab-fade" mode="out-in">
      <div v-if="activeTab === 'account'" key="account" class="tab-panel">

        <div class="card">
          <div class="card-head">
            <h3 class="card-title">{{ t('settings.account.accountInfo') }}</h3>
            <p class="card-sub">{{ t('settings.account.accountInfoSub') }}</p>
          </div>

          <div class="field-grid">
            <div class="field">
              <label>{{ t('settings.account.fullName') }}</label>
              <input v-model="fullName" placeholder="John Doe" />
            </div>
            <div class="field">
              <label>{{ t('settings.account.username') }}</label>
              <input v-model="username" placeholder="johndoe" />
            </div>
          </div>

          <div class="field">
            <label>{{ t('settings.account.language') }}</label>
            <select v-model="language">
              <option value="en">{{ t('settings.account.languageEn') }}</option>
              <option value="el">{{ t('settings.account.languageEl') }}</option>
            </select>
          </div>

          <button class="btn-primary" :disabled="loading" @click="saveAccount">
            <span v-if="loading" class="spinner" />
            {{ t('settings.account.saveChanges') }}
          </button>
        </div>

        <div class="card">
          <div class="card-head">
            <h3 class="card-title">{{ t('settings.account.email') }}</h3>
            <p class="card-sub">{{ t('settings.account.emailSub') }}</p>
          </div>
          <div class="field-row">
            <input v-model="email" type="email" placeholder="email@example.com" class="flex-1" />
            <button class="btn-outline" @click="changeEmail">{{ t('settings.account.updateEmail') }}</button>
          </div>
        </div>

      </div>

      <!-- Security Tab -->
      <div v-else-if="activeTab === 'security'" key="security" class="tab-panel">

        <div class="card">
          <div class="card-head">
            <h3 class="card-title">{{ t('settings.security.changePassword') }}</h3>
            <p class="card-sub">{{ t('settings.security.changePasswordSub') }}</p>
          </div>

          <div class="field">
            <label>{{ t('settings.security.newPassword') }}</label>
            <div class="input-icon-wrap">
              <input v-model="newPassword" :type="showPass ? 'text' : 'password'" placeholder="••••••••" />
              <button class="input-icon-btn" @click="showPass = !showPass">
                <svg v-if="!showPass" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              </button>
            </div>
          </div>

          <div class="field">
            <label>{{ t('settings.security.confirmPassword') }}</label>
            <input
              v-model="confirmPass"
              type="password"
              placeholder="••••••••"
              :class="{ 'input-error': !passwordsMatch }"
            />
            <p v-if="!passwordsMatch" class="field-error">{{ t('settings.security.passwordMismatch') }}</p>
          </div>

          <button class="btn-primary" :disabled="!newPassword || !passwordsMatch" @click="changePassword">
            {{ t('settings.security.updatePassword') }}
          </button>
        </div>

        <div class="card card--danger">
          <div class="card-head">
            <h3 class="card-title card-title--danger">{{ t('settings.security.dangerZone') }}</h3>
            <p class="card-sub">{{ t('settings.security.deleteWarning') }}</p>
          </div>
          <div class="field">
            <label>{{ t('settings.security.deleteConfirmLabel') }}</label>
            <input v-model="deleteConfirm" :placeholder="t('settings.security.deleteConfirmPlaceholder')" class="input-mono" />
          </div>
          <button class="btn-danger" :disabled="deleteConfirm !== 'DELETE'" @click="deleteAccount">
            {{ t('settings.security.confirmDelete') }}
          </button>
        </div>

      </div>
    </Transition>

  </div>
</template>

<style scoped>
.settings {
  padding: 2rem 2.5rem;
  background: var(--bg);
  color: var(--text);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 800px;
}

/* Toast */
.toast {
  position: fixed;
  top: 1.25rem; right: 1.25rem;
  z-index: 200;
  display: flex; align-items: center; gap: .5rem;
  padding: .6rem 1rem;
  border-radius: 10px;
  font-size: .82rem;
  font-weight: 500;
  box-shadow: var(--shadow-lg);
}
.toast--success { background: var(--green-bg); border: 1px solid rgba(58,184,122,.3); color: var(--green); }
.toast--error   { background: var(--red-bg);   border: 1px solid rgba(224,85,85,.3);  color: var(--red); }

.toast-slide-enter-active { transition: all .25s cubic-bezier(.2,.8,.3,1); }
.toast-slide-leave-active { transition: all .15s ease; }
.toast-slide-enter-from { opacity: 0; transform: translateX(20px); }
.toast-slide-leave-to   { opacity: 0; transform: translateX(10px); }

/* Header */
.settings-header { display: flex; align-items: center; }
.avatar-block { display: flex; align-items: center; gap: 1rem; }
.avatar-xl {
  width: 52px; height: 52px;
  background: linear-gradient(135deg, var(--teal-dark), #0a3a3a);
  border: 1px solid var(--border-mid);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; font-weight: 700; color: var(--teal);
  flex-shrink: 0;
}
.avatar-name  { font-size: .95rem; font-weight: 700; color: var(--text); margin: 0; }
.avatar-email { font-size: .72rem; color: var(--text-muted); margin: .1rem 0 0; }

/* Tabs */
.tabs {
  display: flex;
  gap: .3rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: .3rem;
}
.tab-btn {
  display: flex; align-items: center; gap: .45rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: .8rem;
  font-weight: 500;
  padding: .5rem .9rem;
  border-radius: var(--r);
  cursor: pointer;
  transition: background .15s, color .15s;
  flex: 1; justify-content: center;
}
.tab-btn:hover { background: var(--bg-hover); color: var(--text); }
.tab-btn--active { background: var(--bg-hover); color: var(--text); border-bottom: 2px solid var(--teal); }

/* Tab panel */
.tab-panel { display: flex; flex-direction: column; gap: 1.25rem; }

/* Cards */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}
.card--danger { border-color: rgba(224,85,85,.25); }

.card-head { display: flex; flex-direction: column; gap: .2rem; }
.card-title { font-size: .9rem; font-weight: 700; color: var(--text); margin: 0; }
.card-title--danger { color: var(--red); }
.card-sub { font-size: .75rem; color: var(--text-muted); margin: 0; }

/* Fields */
.field { display: flex; flex-direction: column; gap: .4rem; }
.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .85rem; }
.field-row { display: flex; align-items: center; gap: .75rem; flex-wrap: wrap; }
.flex-1 { flex: 1; }

label {
  font-size: .72rem;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: .05em;
  text-transform: uppercase;
}

input, select {
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--r);
  color: var(--text);
  padding: .6rem .85rem;
  font-size: .83rem;
  outline: none;
  transition: border-color .15s, box-shadow .15s;
  width: 100%;
  box-sizing: border-box;
}
input:focus, select:focus {
  border-color: var(--teal-dark);
  box-shadow: 0 0 0 3px var(--teal-glow);
}
input::placeholder { color: var(--text-muted); opacity: .6; }
.input-error { border-color: rgba(224,85,85,.5) !important; }
.input-mono { font-family: monospace; }
.field-error { font-size: .72rem; color: var(--red); margin: 0; }

.input-icon-wrap { position: relative; }
.input-icon-wrap input { padding-right: 2.5rem; }
.input-icon-btn {
  position: absolute; right: .75rem; top: 50%;
  transform: translateY(-50%);
  background: transparent; border: none;
  color: var(--text-muted); cursor: pointer;
  transition: color .15s;
}
.input-icon-btn:hover { color: var(--teal); }

/* Buttons */
.btn-primary {
  display: inline-flex; align-items: center; gap: .4rem;
  background: var(--teal);
  border: none;
  color: #0a0a0a;
  border-radius: var(--r);
  padding: .55rem 1.2rem;
  font-size: .82rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity .15s;
  align-self: flex-start;
}
.btn-primary:hover:not(:disabled) { opacity: .85; }
.btn-primary:disabled { opacity: .3; cursor: not-allowed; }

.btn-outline {
  display: inline-flex; align-items: center; gap: .4rem;
  background: transparent;
  border: 1px solid var(--border-mid);
  color: var(--text-sub);
  border-radius: var(--r);
  padding: .55rem 1.1rem;
  font-size: .82rem;
  cursor: pointer;
  transition: border-color .15s, color .15s;
  white-space: nowrap;
}
.btn-outline:hover { border-color: var(--teal-dark); color: var(--teal); }

.btn-danger {
  display: inline-flex; align-items: center; gap: .4rem;
  background: rgba(224,85,85,.1);
  border: 1px solid rgba(224,85,85,.3);
  color: var(--red);
  border-radius: var(--r);
  padding: .55rem 1.2rem;
  font-size: .82rem;
  font-weight: 600;
  cursor: pointer;
  align-self: flex-start;
  transition: background .15s;
}
.btn-danger:hover:not(:disabled) { background: rgba(224,85,85,.2); }
.btn-danger:disabled { opacity: .3; cursor: not-allowed; }

.spinner {
  width: 12px; height: 12px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin .6s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

.tab-fade-enter-active { transition: opacity .2s, transform .2s; }
.tab-fade-leave-active { transition: opacity .1s; }
.tab-fade-enter-from  { opacity: 0; transform: translateY(6px); }
.tab-fade-leave-to    { opacity: 0; }
</style>
