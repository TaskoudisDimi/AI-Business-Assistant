<script setup lang="ts">
import { ref } from "vue"

const history = ref([
  { type: "Sales Forecast", date: "2026-03-01", status: "Completed" },
  { type: "Customer Analysis", date: "2026-02-28", status: "Completed" },
  { type: "Marketing Campaign", date: "2026-02-27", status: "Completed" }
])
</script>

<template>
  <div>
    <h1>History</h1>

    <div class="card">
      <div v-for="item in history" :key="item.date" class="entry">
        <div>
          <strong>{{ item.type }}</strong>
          <div class="date">{{ item.date }}</div>
        </div>
        <div>{{ item.status }}</div>
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
.entry {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  border-bottom: 1px solid #334155;
}
.entry:last-child {
  border-bottom: none;
}
.date {
  font-size: 12px;
  color: #94a3b8;
}
</style>