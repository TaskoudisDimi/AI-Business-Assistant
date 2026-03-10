<script setup lang="ts">
import { ref } from "vue"

const platform = ref("instagram")
const tone = ref("professional")
const product = ref("")
const result = ref("")
const loading = ref(false)

const generateCampaign = async () => {
  loading.value = true

  setTimeout(() => {
    result.value = `
🚀 Introducing ${product.value}!

Designed to help your business grow faster and smarter.
Don’t miss out – try it today!

#AI #BusinessGrowth
`
    loading.value = false
  }, 1200)
}
</script>

<template>
  <div>
    <h1>Marketing AI</h1>

    <div class="card">
      <label>Product / Service</label>
      <input v-model="product" />

      <label>Platform</label>
      <select v-model="platform">
        <option value="instagram">Instagram</option>
        <option value="facebook">Facebook</option>
        <option value="linkedin">LinkedIn</option>
      </select>

      <label>Tone</label>
      <select v-model="tone">
        <option value="professional">Professional</option>
        <option value="friendly">Friendly</option>
        <option value="bold">Bold</option>
      </select>

      <button @click="generateCampaign">
        {{ loading ? "Generating..." : "Generate Campaign" }}
      </button>
    </div>

    <div v-if="result" class="card mt">
      <h2>Generated Content</h2>
      <pre>{{ result }}</pre>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: #1e293b;
  padding: 20px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
input, select {
  padding: 8px;
  border-radius: 8px;
  background: #0f172a;
  color: white;
  border: 1px solid #334155;
}
button {
  background: #4f46e5;
  padding: 10px;
  border-radius: 8px;
  border: none;
  color: white;
}
.mt { margin-top: 2rem; }
pre {
  background: #0f172a;
  padding: 10px;
  border-radius: 8px;
}
</style>