<script setup lang="ts">
import { ref } from "vue"

const datasets = ref([
  { id: "1", name: "2024 Sales Data" },
  { id: "2", name: "Online Store Data" }
])

const selectedDataset = ref("")
const horizon = ref(30)
const loading = ref(false)
const result = ref<any>(null)

const runForecast = async () => {
  loading.value = true

  // later: call backend AI endpoint
  setTimeout(() => {
    result.value = {
      predictedRevenue: 32450,
      confidence: 92
    }
    loading.value = false
  }, 1500)
}
</script>

<template>
  <div>
    <h1>Sales Forecast</h1>

    <div class="card">
      <label>Select Dataset</label>
      <select v-model="selectedDataset">
        <option v-for="d in datasets" :key="d.id" :value="d.id">
          {{ d.name }}
        </option>
      </select>

      <label>Forecast Horizon (days)</label>
      <select v-model="horizon">
        <option :value="30">30 Days</option>
        <option :value="60">60 Days</option>
        <option :value="90">90 Days</option>
      </select>

      <button @click="runForecast" :disabled="loading">
        {{ loading ? "Running..." : "Run Forecast" }}
      </button>
    </div>

    <div v-if="result" class="card mt">
      <h2>Results</h2>
      <p>Predicted Revenue: <strong>${{ result.predictedRevenue }}</strong></p>
      <p>Confidence: <strong>{{ result.confidence }}%</strong></p>
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

select {
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

.mt {
  margin-top: 2rem;
}
</style>