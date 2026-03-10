<script setup lang="ts">
import { ref } from "vue"

const stats = ref({
  totalCustomers: 312,
  activeCustomers: 240,
  churnRate: 8.4,
  avgLTV: 420
})

const segments = ref([
  { name: "High Value", size: 42 },
  { name: "Loyal", size: 128 },
  { name: "At Risk", size: 36 },
  { name: "New Customers", size: 106 }
])
</script>

<template>
  <div>
    <h1 class="title">Customer Analysis</h1>

    <!-- KPI -->
    <div class="grid">
      <div class="card">
        <h3>Total Customers</h3>
        <p class="big">{{ stats.totalCustomers }}</p>
      </div>

      <div class="card">
        <h3>Active</h3>
        <p class="big">{{ stats.activeCustomers }}</p>
      </div>

      <div class="card">
        <h3>Churn Rate</h3>
        <p class="big red">{{ stats.churnRate }}%</p>
      </div>

      <div class="card">
        <h3>Avg LTV</h3>
        <p class="big">${{ stats.avgLTV }}</p>
      </div>
    </div>

    <!-- Segments -->
    <div class="card mt">
      <h2>Customer Segments</h2>
      <div class="segments">
        <div v-for="s in segments" :key="s.name" class="segment">
          <strong>{{ s.name }}</strong>
          <span>{{ s.size }} customers</span>
        </div>
      </div>
    </div>

    <!-- AI Insight -->
    <div class="card mt">
      <h2>AI Insight</h2>
      <p>
        36 customers show high churn probability. Consider launching a targeted
        retention campaign.
      </p>
    </div>
  </div>
</template>

<style scoped>
.title { margin-bottom: 2rem; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}
.card {
  background: #1e293b;
  padding: 20px;
  border-radius: 16px;
}
.big { font-size: 26px; font-weight: bold; }
.red { color: #ef4444; }
.mt { margin-top: 2rem; }
.segments { display: flex; flex-direction: column; gap: 8px; }
.segment {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: #0f172a;
  border-radius: 8px;
}
</style>