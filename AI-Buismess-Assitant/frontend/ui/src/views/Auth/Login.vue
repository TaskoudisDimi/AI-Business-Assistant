<script setup lang="ts">
import { ref } from "vue"
import { useAuthStore } from "@/stores/auth"
import { useRouter } from "vue-router"

const email    = ref("")
const password = ref("")
const loading  = ref(false)
const error    = ref("")
const showPass = ref(false)

const auth   = useAuthStore()
const router = useRouter()

const submit = async () => {
  error.value = ""
  if (password.value.length < 6) { error.value = "Τουλάχιστον 6 χαρακτήρες"; return }
  loading.value = true
  try {
    const ok = await auth.login(email.value, password.value)
    if (ok) router.push("/dashboard")
    else error.value = auth.error || "Λάθος στοιχεία"
  } catch (e: any) {
    error.value = e.response?.data?.detail || "Αποτυχία σύνδεσης"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-root">
    <!-- Background grid -->
    <div class="bg-grid" />

    <div class="auth-panel">
      <!-- Brand -->
      <div class="brand">
        <div class="brand-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        <span class="brand-name">AI Assistant</span>
      </div>

      <h1 class="auth-title">Καλώς ήρθες</h1>
      <p class="auth-sub">Σύνδεση στην πλατφόρμα</p>

      <div class="form">
        <div class="field">
          <label>Email</label>
          <input v-model="email" type="email" placeholder="name@company.com" @keydown.enter="submit" />
        </div>

        <div class="field">
          <label>Κωδικός</label>
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
          {{ loading ? "Σύνδεση…" : "Σύνδεση" }}
        </button>
      </div>

      <p class="switch-link">
        Νέος χρήστης;
        <router-link to="/register">Δημιουργία λογαριασμού</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@400;500;600;700&display=swap');

.auth-root {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #050a12;
  font-family: 'Sora', sans-serif;
  padding: 1rem;
  position: relative;
  overflow: hidden;
}

.bg-grid {
  position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(30, 48, 80, .25) 1px, transparent 1px),
    linear-gradient(90deg, rgba(30, 48, 80, .25) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%);
}

.auth-panel {
  background: #080f1e;
  border: 1px solid #0e1e33;
  border-radius: 20px;
  padding: 2.5rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 30px 80px rgba(0,0,0,.6);
  position: relative;
  z-index: 1;
}

.brand { display: flex; align-items: center; gap: .65rem; margin-bottom: 2rem; }
.brand-icon {
  width: 38px; height: 38px;
  background: linear-gradient(135deg, #1a3460, #0d1f3e);
  border: 1px solid #1e3a5f; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; color: #4a9eff;
}
.brand-name { font-size: .92rem; font-weight: 700; color: #c8daf5; letter-spacing: -.02em; }

.auth-title { font-size: 1.5rem; font-weight: 700; color: #e8f0fe; margin: 0; letter-spacing: -.03em; }
.auth-sub   { font-size: .8rem; color: #2a4060; margin: .3rem 0 2rem; }

.form { display: flex; flex-direction: column; gap: 1.1rem; }

.field { display: flex; flex-direction: column; gap: .4rem; }
label { font-size: .68rem; font-weight: 600; color: #2a4060; letter-spacing: .07em; text-transform: uppercase; font-family: 'DM Mono', monospace; }

input {
  background: #050a12; border: 1px solid #0e1e33; border-radius: 10px;
  color: #c8d6e8; padding: .7rem .95rem; font-size: .85rem;
  font-family: 'Sora', sans-serif; outline: none; width: 100%; box-sizing: border-box;
  transition: border-color .15s, box-shadow .15s;
}
input:focus { border-color: #2a5299; box-shadow: 0 0 0 3px #2a529920; }
input::placeholder { color: #1e3a5a; }

.input-wrap { position: relative; }
.input-wrap input { padding-right: 2.8rem; }
.toggle-pass {
  position: absolute; right: .8rem; top: 50%; transform: translateY(-50%);
  background: transparent; border: none; color: #2a4060; cursor: pointer;
  transition: color .15s; padding: 0;
}
.toggle-pass:hover { color: #5a8acc; }

.error-msg {
  font-size: .78rem; color: #f07070;
  background: #1f0a0a; border: 1px solid #3d1515;
  border-radius: 8px; padding: .55rem .8rem; margin: 0;
}

.btn-submit {
  display: flex; align-items: center; justify-content: center; gap: .5rem;
  background: linear-gradient(135deg, #1a3a6a, #1a2a58);
  border: 1px solid #2a4a8a; color: #a0c8ff;
  border-radius: 10px; padding: .75rem;
  font-size: .88rem; font-weight: 600; font-family: 'Sora', sans-serif;
  cursor: pointer; transition: background .15s, box-shadow .15s;
  box-shadow: 0 4px 20px rgba(74,158,255,.15);
}
.btn-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #22448a, #1a3468);
  box-shadow: 0 4px 24px rgba(74,158,255,.3);
}
.btn-submit:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }

.switch-link {
  text-align: center; margin-top: 1.5rem;
  font-size: .8rem; color: #2a4060;
}
.switch-link a { color: #4a9eff; text-decoration: none; font-weight: 600; }
.switch-link a:hover { color: #7ab8ff; }

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