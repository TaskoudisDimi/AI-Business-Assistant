<script setup lang="ts">
import { ref, onMounted } from "vue"
import { api } from "@/services/api"

const stats = ref({
  totalRevenue: 0,
  forecastNextMonth: 0,
  customers: 0,
  growth: 0
})

onMounted(async () => {
  // mock for now
  stats.value = {
    totalRevenue: 24500,
    forecastNextMonth: 28700,
    customers: 312,
    growth: 12.4
  }
})
</script>

<template>
  <div>
    <h1 class="title">Dashboard</h1>

    <!-- KPI GRID -->
    <div class="grid">
      <div class="card">
        <h3>Total Revenue</h3>
        <p class="big">${{ stats.totalRevenue }}</p>
      </div>

      <div class="card">
        <h3>Forecast Next Month</h3>
        <p class="big">${{ stats.forecastNextMonth }}</p>
      </div>

      <div class="card">
        <h3>Customers</h3>
        <p class="big">{{ stats.customers }}</p>
      </div>

      <div class="card">
        <h3>Growth</h3>
        <p class="big green">+{{ stats.growth }}%</p>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="card mt">
      <h2>Quick Actions</h2>
      <div class="actions">
        <router-link to="/sales" class="btn">Run Sales Forecast</router-link>
        <router-link to="/datasets" class="btn">Upload Dataset</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.title {
  margin-bottom: 2rem;
}

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

.big {
  font-size: 28px;
  font-weight: bold;
}

.green {
  color: #22c55e;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  background: #4f46e5;
  padding: 10px 16px;
  border-radius: 8px;
  text-decoration: none;
  color: white;
}

.mt {
  margin-top: 2rem;
}
</style>