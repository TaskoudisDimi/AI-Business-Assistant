<script setup lang="ts">
import { ref } from "vue"

const datasets = ref<any[]>([])
const uploading = ref(false)

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files?.length) return

  const file = target.files[0]
  const formData = new FormData()
  if (file) {
    formData.append("file", file)
  }

  uploading.value = true

  await fetch("/api/upload", {
    method: "POST",
    body: formData
  })

  if (file) {
    datasets.value.push({
      name: file.name,
      status: "Processing"
    })
  }

  uploading.value = false
}
</script>

<template>
  <div>
    <h1>Datasets</h1>

    <div class="card">
      <input type="file" @change="handleFileUpload" />
      <p v-if="uploading">Uploading...</p>
    </div>

    <div v-if="datasets.length" class="card mt">
      <h2>Uploaded Datasets</h2>
      <div v-for="d in datasets" :key="d.name" class="dataset">
        <span>{{ d.name }}</span>
        <span>{{ d.status }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: #1e293b;
  padding: 20px;
  border-radius: 16px;
}
.mt { margin-top: 2rem; }
.dataset {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: #0f172a;
  border-radius: 8px;
  margin-top: 6px;
}
</style>