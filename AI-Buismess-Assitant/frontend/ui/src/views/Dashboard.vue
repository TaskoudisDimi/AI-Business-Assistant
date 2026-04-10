<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()

const stats = ref<Record<'totalRevenue' | 'forecastNextMonth' | 'customers' | 'growth', number>>({
  totalRevenue: 0,
  forecastNextMonth: 0,
  customers: 0,
  growth: 0
})

const loaded = ref(false)

onMounted(async () => {
  // Replace with real API call when ready
  await new Promise(r => setTimeout(r, 600))
  stats.value = {
    totalRevenue: 24500,
    forecastNextMonth: 28700,
    customers: 312,
    growth: 12.4
  }
  loaded.value = true
})

const kpis = [
  {
    key: "totalRevenue",
    label: "Total Revenue",
    prefix: "$",
    suffix: "",
    color: "#4a9eff",
    glow: "#4a9eff",
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>`
  },
  {
    key: "forecastNextMonth",
    label: "Forecast Next Month",
    prefix: "$",
    suffix: "",
    color: "#a78bfa",
    glow: "#7c3aed",
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>`
  },
  {
    key: "customers",
    label: "Customers",
    prefix: "",
    suffix: "",
    color: "#34d399",
    glow: "#059669",
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>`
  },
  {
    key: "growth",
    label: "Growth",
    prefix: "+",
    suffix: "%",
    color: "#fbbf24",
    glow: "#d97706",
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`
  }
]

const quickActions = [
  { label: "Sales Forecast", path: "/sales",    desc: "Εκτέλεση πρόβλεψης πωλήσεων", icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>` },
  { label: "Upload Dataset", path: "/datasets", desc: "Εισαγωγή νέου αρχείου CSV",     icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>` },
  { label: "Customers",      path: "/customers",desc: "Ανάλυση πελατολογίου",          icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>` },
  { label: "Marketing AI",   path: "/marketing",desc: "Δημιουργία καμπάνιας",          icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>` },
]

const fmt = (val: number) => val.toLocaleString("el-GR")
</script>

<template>
  <div class="dash">

    <!-- Greeting -->
    <div class="dash-greeting">
      <div>
        <h1 class="greeting-title">
          Καλώς ήρθες, {{ auth.user?.full_name?.split(" ")[0] || "User" }} 👋
        </h1>
        <p class="greeting-sub">
          Εδώ είναι η επισκόπηση για <strong>{{ auth.currentBusiness?.name }}</strong>
        </p>
      </div>
      <div class="greeting-badge">
        <span class="greeting-dot" />
        Live
      </div>
    </div>

    <!-- KPI Grid -->
    <div class="kpi-grid">
      <div
        v-for="(kpi, i) in kpis"
        :key="kpi.key"
        class="kpi-card"
        :style="{ animationDelay: `${i * 80}ms`, '--glow': kpi.glow, '--color': kpi.color }"
      >
        <div class="kpi-top">
          <div class="kpi-icon" :style="{ color: kpi.color, borderColor: kpi.color + '33', background: kpi.color + '10' }" v-html="kpi.icon" />
          <span class="kpi-label">{{ kpi.label }}</span>
        </div>

        <div class="kpi-value" :style="{ color: kpi.color }">
          <span v-if="loaded">{{ kpi.prefix }}{{ fmt(stats[kpi.key as keyof typeof stats]) }}{{ kpi.suffix }}</span>
          <span v-else class="kpi-skeleton" />
        </div>

        <div class="kpi-bar">
          <div
            class="kpi-bar-fill"
            :style="{ width: loaded ? '60%' : '0%', background: `linear-gradient(90deg, ${kpi.color}66, ${kpi.color})` }"
          />
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="section-header">
      <h2 class="section-title">Γρήγορες ενέργειες</h2>
      <div class="section-line" />
    </div>

    <div class="actions-grid">
      <router-link
        v-for="(a, i) in quickActions"
        :key="a.path"
        :to="a.path"
        class="action-card"
        :style="{ animationDelay: `${200 + i * 60}ms` }"
      >
        <div class="action-icon" v-html="a.icon" />
        <div>
          <p class="action-label">{{ a.label }}</p>
          <p class="action-desc">{{ a.desc }}</p>
        </div>
        <svg class="action-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
        </svg>
      </router-link>
    </div>

  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@400;500;600;700&display=swap');

.dash {
  min-height: 100vh;
  padding: 2rem 2.5rem;
  background: #080d16;
  font-family: 'Sora', sans-serif;
  color: #c8d6e8;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Greeting */
.dash-greeting {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}
.greeting-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #e8f0fe;
  margin: 0;
  letter-spacing: -.03em;
}
.greeting-sub {
  font-size: .82rem;
  color: #2a4060;
  margin: .35rem 0 0;
}
.greeting-sub strong { color: #3a6090; }
.greeting-badge {
  display: flex; align-items: center; gap: .4rem;
  background: #0d2a1a;
  border: 1px solid #1a4a30;
  color: #3a9a60;
  font-size: .72rem;
  font-weight: 600;
  padding: .3rem .75rem;
  border-radius: 999px;
  font-family: 'DM Mono', monospace;
}
.greeting-dot {
  width: 6px; height: 6px;
  background: #3a9a60;
  border-radius: 50%;
  box-shadow: 0 0 8px #3a9a60;
  animation: pulse-dot 2s ease infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: .3; }
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}
.kpi-card {
  background: #0a1220;
  border: 1px solid #111e33;
  border-radius: 14px;
  padding: 1.4rem;
  display: flex;
  flex-direction: column;
  gap: .9rem;
  animation: cardIn .4s ease both;
  transition: border-color .2s, box-shadow .2s;
}
.kpi-card:hover {
  border-color: var(--color, #4a9eff)33;
  box-shadow: 0 0 20px var(--glow, #4a9eff)11;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

.kpi-top { display: flex; align-items: center; gap: .65rem; }
.kpi-icon {
  width: 34px; height: 34px;
  border-radius: 9px;
  border-width: 1px;
  border-style: solid;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.kpi-label {
  font-size: .75rem;
  color: #2a4060;
  font-weight: 500;
  letter-spacing: .02em;
}

.kpi-value {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -.03em;
  font-family: 'DM Mono', monospace;
  line-height: 1;
}
.kpi-skeleton {
  display: block;
  width: 100px; height: 28px;
  background: #111e33;
  border-radius: 6px;
  animation: shimmer 1.2s ease infinite;
}
@keyframes shimmer {
  0%, 100% { opacity: .4; }
  50% { opacity: .8; }
}

.kpi-bar {
  height: 3px;
  background: #111e33;
  border-radius: 99px;
  overflow: hidden;
}
.kpi-bar-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 1s cubic-bezier(.4,0,.2,1) .3s;
}

/* Section header */
.section-header {
  display: flex; align-items: center; gap: 1rem;
}
.section-title {
  font-size: .82rem;
  font-weight: 600;
  color: #2a4060;
  margin: 0;
  white-space: nowrap;
  letter-spacing: .05em;
  text-transform: uppercase;
  font-family: 'DM Mono', monospace;
}
.section-line {
  flex: 1; height: 1px;
  background: linear-gradient(90deg, #111e33, transparent);
}

/* Actions grid */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: .75rem;
}
.action-card {
  display: flex;
  align-items: center;
  gap: .85rem;
  background: #0a1220;
  border: 1px solid #111e33;
  border-radius: 12px;
  padding: 1.1rem 1.2rem;
  text-decoration: none;
  color: #5a8acc;
  animation: cardIn .4s ease both;
  transition: background .15s, border-color .15s, color .15s;
}
.action-card:hover {
  background: #0d1f38;
  border-color: #1a3460;
  color: #a0c8f0;
}
.action-icon {
  width: 36px; height: 36px;
  background: #0e1f38;
  border: 1px solid #162a48;
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  color: #3a6fcc;
  flex-shrink: 0;
}
.action-label {
  font-size: .84rem;
  font-weight: 600;
  margin: 0;
  color: #8ab4d8;
}
.action-desc {
  font-size: .72rem;
  color: #2a4060;
  margin: .15rem 0 0;
  font-family: 'DM Mono', monospace;
}
.action-arrow {
  margin-left: auto;
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity .15s, transform .15s;
  flex-shrink: 0;
}
.action-card:hover .action-arrow {
  opacity: 1;
  transform: translateX(0);
}
</style>