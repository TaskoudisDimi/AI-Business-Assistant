<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'

const auth  = useAuthStore()
const { t } = useI18n()

const stats = ref({ totalRevenue: 0, forecastNextMonth: 0, customers: 0, growth: 0 })
const loaded = ref(false)

onMounted(async () => {
  await new Promise(r => setTimeout(r, 500))
  stats.value = { totalRevenue: 24500, forecastNextMonth: 28700, customers: 312, growth: 12.4 }
  loaded.value = true
})

const kpis = [
  {
    key: 'totalRevenue',
    label: () => t('dashboard.kpi.totalRevenue'),
    prefix: '€', suffix: '',
    color: 'var(--teal)',
    icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>`,
  },
  {
    key: 'forecastNextMonth',
    label: () => t('dashboard.kpi.forecastNextMonth'),
    prefix: '€', suffix: '',
    color: '#a78bfa',
    icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>`,
  },
  {
    key: 'customers',
    label: () => t('dashboard.kpi.customers'),
    prefix: '', suffix: '',
    color: '#34d399',
    icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>`,
  },
  {
    key: 'growth',
    label: () => t('dashboard.kpi.growth'),
    prefix: '+', suffix: '%',
    color: '#f59e0b',
    icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`,
  },
]

const quickActions = [
  {
    label: () => t('nav.salesForecast'),
    path: '/sales',
    desc: () => t('dashboard.actions.salesForecastDesc'),
    icon: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>`,
  },
  {
    label: () => t('dashboard.actions.uploadDataset'),
    path: '/datasets',
    desc: () => t('dashboard.actions.uploadDatasetDesc'),
    icon: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>`,
  },
  {
    label: () => t('nav.customerAnalysis'),
    path: '/customers',
    desc: () => t('dashboard.actions.customersDesc'),
    icon: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>`,
  },
]

const fmt = (val: number) => val.toLocaleString('el-GR')
</script>

<template>
  <div class="dash">

    <!-- Greeting -->
    <div class="greeting">
      <div>
        <h1 class="greeting-title">
          {{ t('dashboard.greeting', { name: auth.user?.full_name?.split(' ')[0] || 'User' }) }}
        </h1>
        <p class="greeting-sub">
          {{ t('dashboard.business', { business: auth.currentBusiness?.name }) }}
        </p>
      </div>
    </div>

    <!-- KPIs -->
    <div class="kpi-grid">
      <div
        v-for="(kpi, i) in kpis"
        :key="kpi.key"
        class="kpi-card"
        :style="{ animationDelay: `${i * 60}ms` }"
      >
        <div class="kpi-head">
          <div class="kpi-icon">
            <span v-html="kpi.icon" />
          </div>
          <span class="kpi-label">{{ kpi.label() }}</span>
        </div>
        <div class="kpi-value">
          <span v-if="loaded">{{ kpi.prefix }}{{ fmt(stats[kpi.key as keyof typeof stats]) }}{{ kpi.suffix }}</span>
          <span v-else class="skeleton" />
        </div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="section-label">{{ t('dashboard.quickActions') }}</div>

    <div class="actions-grid">
      <router-link
        v-for="(a, i) in quickActions"
        :key="a.path"
        :to="a.path"
        class="action-card"
        :style="{ animationDelay: `${180 + i * 50}ms` }"
      >
        <div class="action-icon" v-html="a.icon" />
        <div class="action-body">
          <p class="action-label">{{ a.label() }}</p>
          <p class="action-desc">{{ a.desc() }}</p>
        </div>
        <svg class="action-arrow" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="5" y1="12" x2="19" y2="12"/>
          <polyline points="12 5 19 12 12 19"/>
        </svg>
      </router-link>
    </div>

  </div>
</template>

<style scoped>
.dash {
  padding: 2rem 2rem;
  background: var(--bg);
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

/* Greeting */
.greeting-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text);
  margin: 0;
  letter-spacing: -.02em;
}
.greeting-sub {
  font-size: .8rem;
  color: var(--text-muted);
  margin: .25rem 0 0;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: .85rem;
}
.kpi-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: .75rem;
  animation: fadeUp .35s ease both;
  transition: border-color .2s;
}
.kpi-card:hover { border-color: var(--border-mid); }

.kpi-head { display: flex; align-items: center; gap: .55rem; }
.kpi-icon {
  width: 30px; height: 30px;
  background: var(--bg-hover);
  border-radius: var(--r);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  color: var(--text-sub);
}
.kpi-label {
  font-size: .73rem;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: .01em;
}

.kpi-value {
  font-size: 1.65rem;
  font-weight: 700;
  letter-spacing: -.03em;
  line-height: 1;
  font-variant-numeric: tabular-nums;
  color: var(--text);
}
.skeleton {
  display: block;
  width: 90px; height: 26px;
  background: var(--bg-hover);
  border-radius: var(--r);
  animation: shimmer 1.2s ease infinite;
}

/* Section label */
.section-label {
  font-size: .72rem;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: .07em;
  text-transform: uppercase;
}

/* Actions */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: .65rem;
}
.action-card {
  display: flex;
  align-items: center;
  gap: .8rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 1rem 1.1rem;
  text-decoration: none;
  animation: fadeUp .35s ease both;
  transition: background .15s, border-color .15s;
}
.action-card:hover { background: var(--bg-hover); border-color: var(--border-mid); }

.action-icon {
  width: 34px; height: 34px;
  background: var(--bg-hover);
  border: 1px solid var(--border-mid);
  border-radius: var(--r);
  display: flex; align-items: center; justify-content: center;
  color: var(--text-sub);
  flex-shrink: 0;
}
.action-body { flex: 1; }
.action-label {
  font-size: .83rem;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}
.action-desc {
  font-size: .72rem;
  color: var(--text-muted);
  margin: .12rem 0 0;
}
.action-arrow {
  color: var(--text-muted);
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity .15s, transform .15s;
  flex-shrink: 0;
}
.action-card:hover .action-arrow { opacity: 1; transform: translateX(0); }

/* Animations */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
  0%, 100% { opacity: .35; }
  50%       { opacity: .65; }
}
</style>
