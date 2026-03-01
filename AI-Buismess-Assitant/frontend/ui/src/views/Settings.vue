<script setup lang="ts">
import { ref, onMounted, watch } from "vue"
import { useI18n } from "vue-i18n"
import { api } from "@/services/api"

const { t, locale } = useI18n()

// =======================
// Types
// =======================

interface Business {
  id: string
  name: string
  industry: string | null
}

interface User {
  id: string
  full_name: string
  username: string
  email: string
  language: string | null
}

// =======================
// State
// =======================

const loading = ref(false)

const fullName = ref<string>("")
const username = ref<string>("")
const email = ref<string>("")
const language = ref<string>("en")
const newPassword = ref<string>("")

const businesses = ref<Business[]>([])
const activeBusinessId = ref<string>("")
const businessName = ref<string>("")
const industry = ref<string>("")

// =======================
// Load Data
// =======================

onMounted(async () => {
  const { data } = await api.get("/api/me")

  const user: User = data.user

  fullName.value = user.full_name ?? ""
  username.value = user.username ?? ""
  email.value = user.email ?? ""
  language.value = user.language ?? "en"

  businesses.value = data.businesses ?? []

  if (businesses.value.length > 0) {
    const first = businesses.value[0]
    activeBusinessId.value = first?.id ?? ""
    businessName.value = first?.id ?? ""
    industry.value = first?.id ?? ""
  }
})

// =======================
// Watch Business Switch
// =======================

watch(activeBusinessId, (newId) => {
  const selected = businesses.value.find(b => b.id === newId)
  if (selected) {
    businessName.value = selected.name ?? ""
    industry.value = selected.industry ?? ""
  }
})

// =======================
// Actions
// =======================

const saveAccount = async () => {
  loading.value = true

  await api.patch("/api/user", {
    full_name: fullName.value,
    username: username.value,
    language: language.value
  })

  locale.value = language.value
  loading.value = false
}

const changeEmail = async () => {
  await api.patch("/api/user/email", {
    email: email.value
  })
}

const changePassword = async () => {
  if (!newPassword.value) return

  await api.patch("/api/user/password", {
    password: newPassword.value
  })

  newPassword.value = ""
}

const saveBusiness = async () => {
  if (!activeBusinessId.value) return

  loading.value = true

  await api.patch(`/api/businesses/${activeBusinessId.value}`, {
    name: businessName.value,
    industry: industry.value
  })

  loading.value = false
}
</script>

<template>
  <div class="settings">
    <h1>{{ t("settings") }}</h1>

    <!-- ACCOUNT -->
    <div class="card">
      <h2>Account</h2>

      <label>Full Name</label>
      <input v-model="fullName" />

      <label>Username</label>
      <input v-model="username" />

      <label>Email</label>
      <input v-model="email" />
      <button @click="changeEmail">Update Email</button>

      <label>Language</label>
      <select v-model="language">
        <option value="en">English</option>
        <option value="el">Ελληνικά</option>
      </select>

      <button @click="saveAccount" :disabled="loading">
        Save Account
      </button>

      <hr />

      <h3>Change Password</h3>
      <input
        type="password"
        v-model="newPassword"
        placeholder="New password"
      />
      <button @click="changePassword">
        Change Password
      </button>
    </div>

    <!-- BUSINESS -->
    <div class="card">
      <h2>Business</h2>

      <label>Select Business</label>
      <select v-model="activeBusinessId">
        <option
          v-for="b in businesses"
          :key="b.id"
          :value="b.id"
        >
          {{ b.name }}
        </option>
      </select>

      <label>Business Name</label>
      <input v-model="businessName" />

      <label>Industry</label>
      <input v-model="industry" />

      <button @click="saveBusiness" :disabled="loading">
        Save Business
      </button>
    </div>
  </div>
</template>

<style scoped>
.settings {
  max-width: 800px;
}

.card {
  background: #1e293b;
  padding: 2rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

input, select {
  padding: 8px;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #0f172a;
  color: white;
}

button {
  margin-top: 10px;
  padding: 10px;
  border-radius: 8px;
  background: #344149;
  border: none;
  color: white;
  cursor: pointer;
}
</style>