<script setup lang="ts">
import { ref, computed, watch } from "vue"
import { useAuthStore } from "@/stores/auth"
import { api } from "@/services/api"

const auth = useAuthStore()

const loading = ref(false)

/* =========================
   ACCOUNT
========================= */

const fullName = ref("")
const username = ref("")
const email = ref("")
const language = ref("en")
const newPassword = ref("")

watch(
  () => auth.user,
  (u) => {
    if (!u) return
    fullName.value = u.full_name ?? ""
    username.value = u.username ?? ""
    email.value = u.email ?? ""
    language.value = u.language ?? "en"
  },
  { immediate: true }
)

const saveAccount = async () => {
  loading.value = true
  await api.patch("/user", {
    full_name: fullName.value,
    username: username.value,
    language: language.value
  })

  if (auth.user) {
    auth.user.full_name = fullName.value
    auth.user.username = username.value
    auth.user.language = language.value
  }

  loading.value = false
}

const changeEmail = async () => {
  await api.patch("/user/email", { email: email.value })
  if (auth.user) auth.user.email = email.value
}

const changePassword = async () => {
  await api.patch("/user/password", { password: newPassword.value })
  newPassword.value = ""
}

const deleteAccount = async () => {
  if (!confirm("Are you sure?")) return
  await api.delete("/user")
  window.location.href = "/login"
}

/* =========================
   BUSINESS
========================= */

const businesses = ref<any[]>([])
const activeBusinessId = ref("")
const businessName = ref("")
const industry = ref("")

watch(activeBusinessId, () => {
  const b = businesses.value.find(b => b.id === activeBusinessId.value)
  if (!b) return
  businessName.value = b.name
  industry.value = b.industry
})

const saveBusiness = async () => {
  loading.value = true

  await api.patch(`/businesses/${activeBusinessId.value}`, {
    name: businessName.value,
    industry: industry.value
  })

  
  loading.value = false
}

const createBusiness = async () => {
  const { data } = await api.post("/businesses", {
    name: "New Business",
    industry: ""
  })

  activeBusinessId.value = data.id
}
</script>

<template>
  <div class="settings">

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

      <button @click="saveAccount">Save Account</button>

      <hr />

      <h3>Change Password</h3>
      <input type="password" v-model="newPassword" />
      <button @click="changePassword">Change Password</button>

      <hr />

      <button class="danger" @click="deleteAccount">
        Delete Account
      </button>
    </div>

    <!-- BUSINESS -->
    <div class="card">
      <h2>Business</h2>

      <label>Select Business</label>
      <select v-model="activeBusinessId">
        <option v-for="b in businesses" :key="b.id" :value="b.id">
          {{ b.name }}
        </option>
      </select>

      <label>Name</label>
      <input v-model="businessName" />

      <label>Industry</label>
      <input v-model="industry" />

      <button @click="saveBusiness">Save Business</button>
      <button @click="createBusiness">Create New Business</button>
    </div>

  </div>
</template>

<style scoped>
.settings {
  max-width: 900px;
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
  padding: 10px;
  border-radius: 8px;
  background: #344149;
  border: none;
  color: white;
  cursor: pointer;
}

.danger {
  background: #7f1d1d;
}
</style>