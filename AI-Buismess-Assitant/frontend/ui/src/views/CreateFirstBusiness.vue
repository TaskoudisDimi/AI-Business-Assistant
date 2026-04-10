<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'

const auth   = useAuthStore()
const router = useRouter()

const name     = ref('')
const industry = ref('')
const loading  = ref(false)
const error    = ref<string | null>(null)

const industries = [
  'Λιανική', 'Τεχνολογία', 'Υπηρεσίες', 'Εστίαση',
  'Υγεία', 'Εκπαίδευση', 'Κατασκευές', 'Άλλο'
]

const create = async () => {
  if (!name.value.trim()) { error.value = 'Το όνομα είναι υποχρεωτικό'; return }
  loading.value = true; error.value = null
  try {
    await api.post('/businesses', { name: name.value, industry: industry.value || null })
    await auth.fetchUser()
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Αποτυχία δημιουργίας'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="ob-root">
    <div class="bg-grid" />

    <div class="ob-panel">
      <div class="ob-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
      </div>

      <h1 class="ob-title">Δημιούργησε την επιχείρησή σου</h1>
      <p class="ob-sub">
        Για να ξεκινήσεις χρειάζεσαι τουλάχιστον μία επιχείρηση.
        Μπορείς να προσθέσεις περισσότερες αργότερα από τις Ρυθμίσεις.
      </p>

      <div class="form">
        <div class="field">
          <label>Όνομα επιχείρησης *</label>
          <input v-model="name" placeholder="π.χ. Η Εταιρεία μου" @keydown.enter="create" />
        </div>

        <div class="field">
          <label>Κλάδος</label>
          <div class="select-wrap">
            <select v-model="industry">
              <option value="">— Επιλογή κλάδου —</option>
              <option v-for="ind in industries" :key="ind" :value="ind">{{ ind }}</option>
            </select>
            <svg class="sel-arr" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
          </div>
        </div>

        <Transition name="msg">
          <p v-if="error" class="error-msg">{{ error }}</p>
        </Transition>

        <button class="btn-create" :disabled="loading" @click="create">
          <span v-if="loading" class="spinner" />
          {{ loading ? 'Δημιουργία…' : 'Έναρξη →' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@400;500;600;700&display=swap');
.ob-root {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: #050a12; font-family: 'Sora', sans-serif; padding: 1rem;
  position: relative; overflow: hidden;
}
.bg-grid {
  position: absolute; inset: 0; pointer-events: none;
  background-image: linear-gradient(rgba(30,48,80,.25) 1px, transparent 1px), linear-gradient(90deg, rgba(30,48,80,.25) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%);
}
.ob-panel {
  background: #080f1e; border: 1px solid #0e1e33; border-radius: 20px;
  padding: 2.5rem; width: 100%; max-width: 440px;
  box-shadow: 0 30px 80px rgba(0,0,0,.6); position: relative; z-index: 1;
  display: flex; flex-direction: column; gap: 1rem;
}
.ob-icon {
  width: 56px; height: 56px;
  background: linear-gradient(135deg, #1a3460, #0d1f3e);
  border: 1px solid #1e3a5f; border-radius: 14px;
  display: flex; align-items: center; justify-content: center; color: #4a9eff;
  margin-bottom: .25rem;
}
.ob-title { font-size: 1.35rem; font-weight: 700; color: #e8f0fe; margin: 0; letter-spacing: -.03em; }
.ob-sub   { font-size: .8rem; color: #2a4060; margin: 0; line-height: 1.6; }
.form { display: flex; flex-direction: column; gap: 1rem; margin-top: .5rem; }
.field { display: flex; flex-direction: column; gap: .4rem; }
label { font-size: .68rem; font-weight: 600; color: #2a4060; letter-spacing: .07em; text-transform: uppercase; font-family: 'DM Mono', monospace; }
input, select {
  background: #050a12; border: 1px solid #0e1e33; border-radius: 10px;
  color: #c8d6e8; padding: .7rem .95rem; font-size: .85rem;
  font-family: 'Sora', sans-serif; outline: none; width: 100%; box-sizing: border-box;
  appearance: none; transition: border-color .15s, box-shadow .15s;
}
input:focus, select:focus { border-color: #2a5299; box-shadow: 0 0 0 3px #2a529920; }
input::placeholder { color: #1e3a5a; }
.select-wrap { position: relative; }
.sel-arr { position: absolute; right: .85rem; top: 50%; transform: translateY(-50%); color: #2a4060; pointer-events: none; }
.error-msg { font-size: .78rem; color: #f07070; background: #1f0a0a; border: 1px solid #3d1515; border-radius: 8px; padding: .55rem .8rem; margin: 0; }
.btn-create {
  display: flex; align-items: center; justify-content: center; gap: .5rem;
  background: linear-gradient(135deg, #1a3a6a, #1a2a58); border: 1px solid #2a4a8a; color: #a0c8ff;
  border-radius: 10px; padding: .75rem; font-size: .9rem; font-weight: 600; font-family: 'Sora', sans-serif;
  cursor: pointer; transition: background .15s, box-shadow .15s; box-shadow: 0 4px 20px rgba(74,158,255,.15);
}
.btn-create:hover:not(:disabled) { background: linear-gradient(135deg, #22448a, #1a3468); box-shadow: 0 4px 24px rgba(74,158,255,.3); }
.btn-create:disabled { opacity: .4; cursor: not-allowed; }
.spinner { width: 13px; height: 13px; border-radius: 50%; border: 2px solid transparent; border-top-color: currentColor; animation: spin .6s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
.msg-enter-active { transition: all .2s ease; }
.msg-leave-active { transition: all .15s ease; }
.msg-enter-from, .msg-leave-to { opacity: 0; transform: translateY(-4px); }
</style>