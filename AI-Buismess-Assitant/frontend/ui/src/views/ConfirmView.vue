<script setup lang="ts">
import { onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"

const message = ref("Confirming...")
const router = useRouter()

onMounted(async () => {
  try {
    await axios.get("http://127.0.0.1:8000/api/auth/me", {
      withCredentials: true,
    })
    message.value = "Email verified successfully!"
  } catch {
    message.value = "Verification failed."
  }

  setTimeout(() => {
    router.push("/login")
  }, 3000)
})
</script>

<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <h2>{{ message }}</h2>
    </div>
  </div>
</template>