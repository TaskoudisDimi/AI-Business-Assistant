<script setup lang="ts">
import { ref, computed, watch } from "vue"
import { useAuthStore } from "@/stores/auth"
import { api } from "@/services/api"

const auth = useAuthStore()

const loading  = ref(false)
const toast    = ref<{ msg: string; type: "success" | "error" } | null>(null)
const activeTab = ref<"account" | "security" | "business">("account")

const showToast = (msg: string, type: "success" | "error" = "success") => {
  toast.value = { msg, type }
  setTimeout(() => (toast.value = null), 3000)
}

/* ── Account ── */
const fullName = ref("")
const username = ref("")
const email    = ref("")
const language = ref("en")

watch(() => auth.user, (u) => {
  if (!u) return
  fullName.value = u.full_name ?? ""
  username.value = u.username ?? ""
  email.value    = u.email ?? ""
  language.value = u.language ?? "en"
}, { immediate: true })

const saveAccount = async () => {
  loading.value = true
  try {
    await api.patch("/user", { full_name: fullName.value, username: username.value, language: language.value })
    if (auth.user) {
      auth.user.full_name = fullName.value
      auth.user.username  = username.value
      auth.user.language  = language.value
    }
    showToast("Αποθηκεύτηκε!")
  } catch { showToast("Αποτυχία αποθήκευσης", "error") }
  finally  { loading.value = false }
}

const changeEmail = async () => {
  try {
    await api.patch("/user/email", { email: email.value })
    if (auth.user) auth.user.email = email.value
    showToast("Email ενημερώθηκε")
  } catch { showToast("Αποτυχία", "error") }
}

/* ── Security ── */
const newPassword    = ref("")
const confirmPass    = ref("")
const showPass       = ref(false)
const deleteConfirm  = ref("")

const passwordsMatch = computed(() => !confirmPass.value || newPassword.value === confirmPass.value)

const changePassword = async () => {
  if (!passwordsMatch.value) return
  try {
    await api.patch("/user/password", { password: newPassword.value })
    newPassword.value = ""; confirmPass.value = ""
    showToast("Κωδικός άλλαξε")
  } catch { showToast("Αποτυχία", "error") }
}

const deleteAccount = async () => {
  if (deleteConfirm.value !== "DELETE") return
  await api.delete("/user")
  window.location.href = "/login"
}

/* ── Business ── */
const activeBusinessId = ref(auth.currentBusinessId ?? "")
const businessName     = ref("")
const industry         = ref("")

watch(activeBusinessId, () => {
  const b = auth.businesses.find(b => b.id === activeBusinessId.value)
  if (!b) return
  businessName.value = b.name
  industry.value     = b.industry ?? ""
}, { immediate: true })

const saveBusiness = async () => {
  loading.value = true
  try {
    await api.patch(`/businesses/${activeBusinessId.value}`, { name: businessName.value, industry: industry.value })
    showToast("Επιχείρηση αποθηκεύτηκε")
  } catch { showToast("Αποτυχία", "error") }
  finally  { loading.value = false }
}

const createBusiness = async () => {
  try {
    const { data } = await api.post("/businesses", { name: "Νέα Επιχείρηση", industry: "" })
    activeBusinessId.value = data.id
    showToast("Δημιουργήθηκε!")
  } catch { showToast("Αποτυχία", "error") }
}

const initials = computed(() => {
  return (auth.user?.full_name ?? "U").split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2)
})

const tabs = [
  { key: "account",  label: "Λογαριασμός", icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>` },
  { key: "security", label: "Ασφάλεια",    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>` },
  { key: "business", label: "Επιχείρηση",  icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>` },
]
</script>

<template>
  <div class="settings" @click="() => {}">

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
        v-for="t in tabs"
        :key="t.key"
        class="tab-btn"
        :class="{ 'tab-btn--active': activeTab === t.key }"
        @click="activeTab = t.key as any"
      >
        <span v-html="t.icon" />
        {{ t.label }}
      </button>
    </div>

    <!-- ── Account Tab ── -->
    <Transition name="tab-fade" mode="out-in">
      <div v-if="activeTab === 'account'" key="account" class="tab-panel">
        <div class="card">
          <div class="card-head">
            <h3 class="card-title">Πληροφορίες λογαριασμού</h3>
            <p class="card-sub">Ενημέρωσε το όνομα και τις προτιμήσεις σου</p>
          </div>

          <div class="field-grid">
            <div class="field">
              <label>Πλήρες όνομα</label>
              <input v-model="fullName" placeholder="John Doe" />
            </div>
            <div class="field">
              <label>Username</label>
              <input v-model="username" placeholder="johndoe" />
            </div>
          </div>

          <div class="field">
            <label>Γλώσσα</label>
            <select v-model="language">
              <option value="en">English</option>
              <option value="el">Ελληνικά</option>
            </select>
          </div>

          <button class="btn-primary" :disabled="loading" @click="saveAccount">
            <span v-if="loading" class="spinner" />
            Αποθήκευση
          </button>
        </div>

        <div class="card">
          <div class="card-head">
            <h3 class="card-title">Email</h3>
            <p class="card-sub">Αλλαγή διεύθυνσης email</p>
          </div>
          <div class="field-row">
            <input v-model="email" type="email" placeholder="email@example.com" class="flex-1" />
            <button class="btn-outline" @click="changeEmail">Ενημέρωση</button>
          </div>
        </div>
      </div>

      <!-- ── Security Tab ── -->
      <div v-else-if="activeTab === 'security'" key="security" class="tab-panel">
        <div class="card">
          <div class="card-head">
            <h3 class="card-title">Αλλαγή κωδικού</h3>
            <p class="card-sub">Χρησιμοποίησε τουλάχιστον 8 χαρακτήρες</p>
          </div>

          <div class="field">
            <label>Νέος κωδικός</label>
            <div class="input-icon-wrap">
              <input v-model="newPassword" :type="showPass ? 'text' : 'password'" placeholder="••••••••" />
              <button class="input-icon-btn" @click="showPass = !showPass">
                <svg v-if="!showPass" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              </button>
            </div>
          </div>

          <div class="field">
            <label>Επιβεβαίωση κωδικού</label>
            <input
              v-model="confirmPass"
              type="password"
              placeholder="••••••••"
              :class="{ 'input-error': !passwordsMatch }"
            />
            <p v-if="!passwordsMatch" class="field-error">Οι κωδικοί δεν ταιριάζουν</p>
          </div>

          <button class="btn-primary" :disabled="!newPassword || !passwordsMatch" @click="changePassword">
            Αλλαγή κωδικού
          </button>
        </div>

        <div class="card card--danger">
          <div class="card-head">
            <h3 class="card-title card-title--danger">Διαγραφή λογαριασμού</h3>
            <p class="card-sub">Αμετάκλητη ενέργεια. Όλα τα δεδομένα σου θα διαγραφούν.</p>
          </div>
          <div class="field">
            <label>Γράψε <code>DELETE</code> για επιβεβαίωση</label>
            <input v-model="deleteConfirm" placeholder="DELETE" class="input-mono" />
          </div>
          <button
            class="btn-danger"
            :disabled="deleteConfirm !== 'DELETE'"
            @click="deleteAccount"
          >
            Διαγραφή λογαριασμού
          </button>
        </div>
      </div>

      <!-- ── Business Tab ── -->
      <div v-else-if="activeTab === 'business'" key="business" class="tab-panel">
        <div class="card">
          <div class="card-head">
            <h3 class="card-title">Επιλογή επιχείρησης</h3>
          </div>
          <div class="biz-list">
            <button
              v-for="b in auth.businesses"
              :key="b.id"
              class="biz-item"
              :class="{ 'biz-item--active': b.id === activeBusinessId }"
              @click="activeBusinessId = b.id"
            >
              <div class="biz-avatar">{{ b.name.charAt(0).toUpperCase() }}</div>
              <div>
                <p class="biz-name">{{ b.name }}</p>
                <p class="biz-industry">{{ b.industry || 'Χωρίς κλάδο' }}</p>
              </div>
              <span v-if="b.id === activeBusinessId" class="biz-active-tag">Επιλεγμένο</span>
            </button>
          </div>
        </div>

        <div class="card" v-if="activeBusinessId">
          <div class="card-head">
            <h3 class="card-title">Επεξεργασία επιχείρησης</h3>
          </div>
          <div class="field-grid">
            <div class="field">
              <label>Όνομα</label>
              <input v-model="businessName" placeholder="Όνομα επιχείρησης" />
            </div>
            <div class="field">
              <label>Κλάδος</label>
              <input v-model="industry" placeholder="π.χ. Retail, SaaS…" />
            </div>
          </div>
          <div class="field-row">
            <button class="btn-primary" :disabled="loading" @click="saveBusiness">
              <span v-if="loading" class="spinner" />
              Αποθήκευση
            </button>
            <button class="btn-outline" @click="createBusiness">
              + Νέα επιχείρηση
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@400;500;600;700&display=swap');

.settings {
  min-height: 100vh;
  padding: 2rem 2.5rem;
  background: #080d16;
  font-family: 'Sora', sans-serif;
  color: #c8d6e8;
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
  box-shadow: 0 8px 24px rgba(0,0,0,.4);
}
.toast--success { background: #0d2a1a; border: 1px solid #1a4a30; color: #4ade80; }
.toast--error   { background: #1f0a0a; border: 1px solid #3d1515; color: #f87171; }

.toast-slide-enter-active { transition: all .25s cubic-bezier(.2,.8,.3,1); }
.toast-slide-leave-active { transition: all .15s ease; }
.toast-slide-enter-from { opacity: 0; transform: translateX(20px); }
.toast-slide-leave-to   { opacity: 0; transform: translateX(10px); }

/* Header */
.settings-header { display: flex; align-items: center; justify-content: space-between; }
.avatar-block { display: flex; align-items: center; gap: 1rem; }
.avatar-xl {
  width: 52px; height: 52px;
  background: linear-gradient(135deg, #1a3460, #0d244a);
  border: 1px solid #1e3a5f;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; font-weight: 700; color: #7ab8ff;
}
.avatar-name  { font-size: .95rem; font-weight: 700; color: #c8daf5; margin: 0; }
.avatar-email { font-size: .72rem; color: #2a4060; margin: .1rem 0 0; font-family: 'DM Mono', monospace; }

/* Tabs */
.tabs {
  display: flex;
  gap: .35rem;
  background: #0a1220;
  border: 1px solid #111e33;
  border-radius: 12px;
  padding: .35rem;
}
.tab-btn {
  display: flex; align-items: center; gap: .5rem;
  background: transparent;
  border: none;
  color: #3a5a80;
  font-size: .8rem;
  font-weight: 500;
  font-family: 'Sora', sans-serif;
  padding: .5rem .9rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background .15s, color .15s;
  flex: 1; justify-content: center;
}
.tab-btn:hover { background: #0d1f38; color: #7ab0e0; }
.tab-btn--active { background: #0d2040; color: #7ab8ff; }

/* Tab panel */
.tab-panel { display: flex; flex-direction: column; gap: 1.25rem; }

/* Cards */
.card {
  background: #0a1220;
  border: 1px solid #111e33;
  border-radius: 14px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}
.card--danger { border-color: #1f0a0a; }

.card-head { display: flex; flex-direction: column; gap: .2rem; }
.card-title { font-size: .9rem; font-weight: 700; color: #b8d0ec; margin: 0; }
.card-title--danger { color: #cc5050; }
.card-sub { font-size: .75rem; color: #2a4060; margin: 0; }

/* Fields */
.field { display: flex; flex-direction: column; gap: .4rem; }
.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .85rem; }
.field-row { display: flex; align-items: center; gap: .75rem; flex-wrap: wrap; }
.flex-1 { flex: 1; }

label {
  font-size: .72rem;
  font-weight: 600;
  color: #2a4060;
  letter-spacing: .05em;
  text-transform: uppercase;
  font-family: 'DM Mono', monospace;
}
input, select {
  background: #080d16;
  border: 1px solid #111e33;
  border-radius: 9px;
  color: #c8d6e8;
  padding: .6rem .85rem;
  font-size: .83rem;
  font-family: 'Sora', sans-serif;
  outline: none;
  transition: border-color .15s, box-shadow .15s;
  width: 100%;
  box-sizing: border-box;
}
input:focus, select:focus {
  border-color: #2a5299;
  box-shadow: 0 0 0 3px #2a529922;
}
.input-error { border-color: #5a1515 !important; }
.input-mono { font-family: 'DM Mono', monospace; }
.field-error { font-size: .72rem; color: #cc5050; margin: 0; }

code {
  background: #111e33;
  color: #7ab8ff;
  padding: .1rem .35rem;
  border-radius: 4px;
  font-family: 'DM Mono', monospace;
  font-size: .78rem;
}

/* Input with icon */
.input-icon-wrap { position: relative; }
.input-icon-wrap input { padding-right: 2.5rem; }
.input-icon-btn {
  position: absolute; right: .75rem; top: 50%;
  transform: translateY(-50%);
  background: transparent; border: none;
  color: #2a4060; cursor: pointer;
  transition: color .15s;
}
.input-icon-btn:hover { color: #5a8acc; }

/* Buttons */
.btn-primary {
  display: inline-flex; align-items: center; gap: .4rem;
  background: #1a3460;
  border: 1px solid #2a4a7a;
  color: #7ab8ff;
  border-radius: 9px;
  padding: .55rem 1.2rem;
  font-size: .82rem;
  font-weight: 600;
  font-family: 'Sora', sans-serif;
  cursor: pointer;
  transition: background .15s;
  align-self: flex-start;
}
.btn-primary:hover:not(:disabled) { background: #22448a; }
.btn-primary:disabled { opacity: .35; cursor: not-allowed; }

.btn-outline {
  display: inline-flex; align-items: center; gap: .4rem;
  background: transparent;
  border: 1px solid #162035;
  color: #4a6a8a;
  border-radius: 9px;
  padding: .55rem 1.1rem;
  font-size: .82rem;
  font-family: 'Sora', sans-serif;
  cursor: pointer;
  transition: border-color .15s, color .15s;
}
.btn-outline:hover { border-color: #2a4060; color: #7a9cc0; }

.btn-danger {
  display: inline-flex; align-items: center; gap: .4rem;
  background: #3d1515;
  border: 1px solid #5a2020;
  color: #f07070;
  border-radius: 9px;
  padding: .55rem 1.2rem;
  font-size: .82rem;
  font-weight: 600;
  font-family: 'Sora', sans-serif;
  cursor: pointer;
  align-self: flex-start;
  transition: background .15s;
}
.btn-danger:hover:not(:disabled) { background: #5a1a1a; }
.btn-danger:disabled { opacity: .3; cursor: not-allowed; }

/* Spinner */
.spinner {
  width: 12px; height: 12px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin .6s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Business list */
.biz-list { display: flex; flex-direction: column; gap: .5rem; }
.biz-item {
  display: flex; align-items: center; gap: .85rem;
  background: transparent;
  border: 1px solid #111e33;
  border-radius: 10px;
  padding: .8rem 1rem;
  cursor: pointer;
  font-family: 'Sora', sans-serif;
  text-align: left;
  transition: background .15s, border-color .15s;
  width: 100%;
}
.biz-item:hover { background: #0d1f38; border-color: #162a48; }
.biz-item--active { background: #0d2040; border-color: #1a3460; }

.biz-avatar {
  width: 36px; height: 36px;
  background: #0e1f38;
  border: 1px solid #162a48;
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  font-size: .82rem; font-weight: 700; color: #4a9eff;
  flex-shrink: 0;
}
.biz-name     { font-size: .84rem; font-weight: 600; color: #8ab4d8; margin: 0; }
.biz-industry { font-size: .7rem; color: #2a4060; margin: .1rem 0 0; font-family: 'DM Mono', monospace; }
.biz-active-tag {
  margin-left: auto;
  background: #0d2a1a;
  border: 1px solid #1a4a30;
  color: #3a9a60;
  font-size: .65rem;
  padding: .15rem .5rem;
  border-radius: 999px;
  font-family: 'DM Mono', monospace;
}

/* Tab transition */
.tab-fade-enter-active { transition: opacity .2s, transform .2s; }
.tab-fade-leave-active { transition: opacity .1s; }
.tab-fade-enter-from  { opacity: 0; transform: translateY(6px); }
.tab-fade-leave-to    { opacity: 0; }
</style>