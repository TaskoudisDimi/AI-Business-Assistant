<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { api } from '@/services/api'

const auth  = useAuthStore()
const { t } = useI18n()

const stats  = ref({ totalRevenue: 0, forecastNextMonth: 0, customers: 0, growth: 0 })
const loaded = ref(false)
const lowStockCount = ref(0)

onMounted(async () => {
  await new Promise(r => setTimeout(r, 500))
  stats.value = { totalRevenue: 24500, forecastNextMonth: 28700, customers: 312, growth: 12.4 }
  loaded.value = true

  const bizId = auth.currentBusiness?.id
  if (bizId) {
    try {
      const r = await api.get('/inventory/reorder-suggestions', { params: { business_id: bizId } })
      lowStockCount.value = (r.data as { urgency: string }[]).filter(s => s.urgency === 'critical').length
    } catch { /* warehouse tables may not exist yet */ }
  }
})

const kpis = [
  {
    key: 'totalRevenue',
    label: () => t('dashboard.kpi.totalRevenue'),
    prefix: '€', suffix: '',
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>`,
    trend: '+8.2%',
    trendUp: true,
  },
  {
    key: 'forecastNextMonth',
    label: () => t('dashboard.kpi.forecastNextMonth'),
    prefix: '€', suffix: '',
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>`,
    trend: 'AI',
    trendUp: true,
  },
  {
    key: 'customers',
    label: () => t('dashboard.kpi.customers'),
    prefix: '', suffix: '',
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>`,
    trend: '+12',
    trendUp: true,
  },
  {
    key: 'growth',
    label: () => t('dashboard.kpi.growth'),
    prefix: '+', suffix: '%',
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`,
    trend: 'MoM',
    trendUp: true,
  },
]

const quickActions = [
  {
    label: () => t('nav.salesForecast'),
    path: '/sales',
    desc: () => t('dashboard.actions.salesForecastDesc'),
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>`,
  },
  {
    label: () => t('dashboard.actions.uploadDataset'),
    path: '/datasets',
    desc: () => t('dashboard.actions.uploadDatasetDesc'),
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>`,
  },
  {
    label: () => t('nav.customerAnalysis'),
    path: '/customers',
    desc: () => t('dashboard.actions.customersDesc'),
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>`,
  },
]

const warehouseActions = [
  {
    label: () => t('nav.inventory'),
    path: '/inventory',
    desc: () => t('dashboard.actions.inventoryDesc'),
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/><line x1="12" y1="12" x2="12" y2="16"/><line x1="10" y1="14" x2="14" y2="14"/></svg>`,
  },
  {
    label: () => t('nav.products'),
    path: '/products',
    desc: () => t('dashboard.actions.productsDesc'),
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>`,
  },
  {
    label: () => t('nav.orders'),
    path: '/orders',
    desc: () => t('dashboard.actions.ordersDesc'),
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="15" y2="17"/></svg>`,
  },
]

const now = computed(() => new Date().toLocaleDateString('el-GR', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' }))
const fmt = (val: number) => val.toLocaleString('el-GR')
</script>

<template>
  <div class="dash">

    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-left">
        <div>
          <h1 class="page-title">
            {{ t('dashboard.greeting', { name: auth.user?.full_name?.split(' ')[0] || 'User' }) }}
          </h1>
          <p class="page-sub">{{ t('dashboard.business', { business: auth.currentBusiness?.name }) }}</p>
        </div>
      </div>
      <div class="page-header-right">
        <span class="date-label">{{ now }}</span>
        <div class="ai-badge">
          <span class="ai-dot" />
          AI Active
        </div>
      </div>
    </div>

    <!-- Section: Performance -->
    <div class="section">
      <p class="section-label">{{ t('dashboard.sectionPerformance').toUpperCase() }}</p>
      <div class="kpi-grid">
        <div
          v-for="(kpi, i) in kpis"
          :key="kpi.key"
          class="kpi-card"
          :style="{ animationDelay: `${i * 60}ms` }"
        >
          <div class="kpi-top">
            <div class="kpi-icon">
              <span v-html="kpi.icon" />
            </div>
            <span class="kpi-trend" :class="kpi.trendUp ? 'trend--up' : 'trend--down'">
              {{ kpi.trend }}
            </span>
          </div>
          <div class="kpi-value">
            <span v-if="loaded">{{ kpi.prefix }}{{ fmt(stats[kpi.key as keyof typeof stats]) }}{{ kpi.suffix }}</span>
            <span v-else class="skeleton" />
          </div>
          <p class="kpi-label">{{ kpi.label() }}</p>
        </div>
      </div>
    </div>

    <!-- Section: Quick Access -->
    <div class="section">
      <p class="section-label">{{ t('dashboard.quickActions') }}</p>
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
          <svg class="action-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"/>
            <polyline points="12 5 19 12 12 19"/>
          </svg>
        </router-link>
      </div>
    </div>

    <!-- Section: Warehouse -->
    <div class="section">
      <div class="section-label-row">
        <p class="section-label">{{ t('dashboard.warehouseAlerts').toUpperCase() }}</p>
        <span v-if="lowStockCount > 0" class="alert-badge">
          {{ lowStockCount }} critical
        </span>
      </div>
      <div class="actions-grid">
        <router-link
          v-for="(a, i) in warehouseActions"
          :key="a.path"
          :to="a.path"
          class="action-card"
          :style="{ animationDelay: `${300 + i * 50}ms` }"
        >
          <div class="action-icon" v-html="a.icon" />
          <div class="action-body">
            <p class="action-label">{{ a.label() }}</p>
            <p class="action-desc">{{ a.desc() }}</p>
          </div>
          <svg class="action-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"/>
            <polyline points="12 5 19 12 12 19"/>
          </svg>
        </router-link>
      </div>
    </div>

  </div>
</template>

<style scoped>
.dash {
  padding: 1.75rem 2rem;
  background: var(--bg);
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border);
}
.page-header-left { display: flex; align-items: center; gap: .75rem; }
.page-header-right { display: flex; align-items: center; gap: .75rem; }
.page-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text);
  margin: 0;
  letter-spacing: -.02em;
}
.page-sub {
  font-size: .73rem;
  color: var(--text-muted);
  margin: .2rem 0 0;
}
.date-label {
  font-size: .7rem;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}
.ai-badge {
  display: flex; align-items: center; gap: .35rem;
  background: rgba(62,207,191,.06);
  border: 1px solid rgba(62,207,191,.18);
  border-radius: 999px;
  padding: .22rem .7rem;
  font-size: .68rem;
  font-weight: 600;
  color: var(--teal);
  letter-spacing: .03em;
}
.ai-dot {
  width: 5px; height: 5px;
  background: var(--teal);
  border-radius: 50%;
  animation: pulse 2s ease infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1 } 50% { opacity: .3 } }

/* Sections */
.section { display: flex; flex-direction: column; gap: .75rem; }
.section-label-row { display: flex; align-items: center; gap: .6rem; }
.section-label {
  font-size: .62rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: .1em;
  text-transform: uppercase;
  margin: 0;
}
.alert-badge {
  font-size: .62rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
  background: var(--red-bg); color: var(--red);
  border: 1px solid rgba(224,85,85,.25); border-radius: 999px;
  padding: .1rem .5rem;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: .75rem;
}
.kpi-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 1.1rem 1.2rem;
  display: flex;
  flex-direction: column;
  gap: .5rem;
  animation: fadeUp .35s ease both;
  transition: border-color .2s;
}
.kpi-card:hover { border-color: var(--border-mid); }

.kpi-top { display: flex; align-items: center; justify-content: space-between; }
.kpi-icon {
  width: 28px; height: 28px;
  background: var(--bg-hover);
  border-radius: var(--r);
  display: flex; align-items: center; justify-content: center;
  color: var(--text-sub);
  flex-shrink: 0;
}
.kpi-trend {
  font-size: .65rem;
  font-weight: 700;
  padding: .12rem .45rem;
  border-radius: 999px;
  letter-spacing: .03em;
}
.trend--up   { background: var(--green-bg); color: var(--green); border: 1px solid rgba(58,184,122,.2); }
.trend--down { background: var(--red-bg);   color: var(--red);   border: 1px solid rgba(224,85,85,.2); }

.kpi-value {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -.03em;
  line-height: 1;
  font-variant-numeric: tabular-nums;
  color: var(--text);
}
.kpi-label {
  font-size: .7rem;
  color: var(--text-muted);
  margin: 0;
  font-weight: 500;
}
.skeleton {
  display: block;
  width: 90px; height: 24px;
  background: var(--bg-hover);
  border-radius: var(--r);
  animation: shimmer 1.2s ease infinite;
}

/* Actions Grid */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: .6rem;
}
.action-card {
  display: flex;
  align-items: center;
  gap: .8rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: .9rem 1rem;
  text-decoration: none;
  animation: fadeUp .35s ease both;
  transition: background .15s, border-color .15s;
}
.action-card:hover { background: var(--bg-hover); border-color: var(--border-mid); }

.action-icon {
  width: 32px; height: 32px;
  background: var(--bg-hover);
  border: 1px solid var(--border-mid);
  border-radius: var(--r);
  display: flex; align-items: center; justify-content: center;
  color: var(--text-sub);
  flex-shrink: 0;
}
.action-body { flex: 1; min-width: 0; }
.action-label {
  font-size: .82rem;
  font-weight: 600;
  color: var(--text);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.action-desc {
  font-size: .7rem;
  color: var(--text-muted);
  margin: .1rem 0 0;
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
