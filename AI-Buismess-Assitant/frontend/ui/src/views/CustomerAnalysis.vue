<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const stats = ref({ total: 312, active: 240, churn: 8.4, ltv: 420 })

const segments = ref([
  { name: 'High Value',    count: 42,  color: 'var(--teal)',  pct: 13 },
  { name: 'Loyal',         count: 128, color: '#34d399',      pct: 41 },
  { name: 'At Risk',       count: 36,  color: '#f59e0b',      pct: 12 },
  { name: 'New Customers', count: 106, color: '#a78bfa',      pct: 34 },
])

const kpis = [
  {
    key: 'total',
    label: () => t('customers.kpi.total'),
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>`,
    fmt: (v: number) => String(v),
  },
  {
    key: 'active',
    label: () => t('customers.kpi.active'),
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`,
    fmt: (v: number) => String(v),
  },
  {
    key: 'churn',
    label: () => t('customers.kpi.churnRate'),
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/></svg>`,
    fmt: (v: number) => v + '%',
  },
  {
    key: 'ltv',
    label: () => t('customers.kpi.avgLtv'),
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>`,
    fmt: (v: number) => '€' + v,
  },
]
</script>

<template>
  <div class="page">

    <div class="page-header">
      <div class="header-icon">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 00-3-3.87"/>
          <path d="M16 3.13a4 4 0 010 7.75"/>
        </svg>
      </div>
      <div>
        <h1 class="page-title">{{ t('customers.title') }}</h1>
        <p class="page-sub">{{ t('customers.subtitle') }}</p>
      </div>
    </div>

    <!-- KPIs -->
    <div class="kpi-grid">
      <div v-for="kpi in kpis" :key="kpi.key" class="kpi">
        <div class="kpi-icon">
          <span v-html="kpi.icon" />
        </div>
        <p class="kpi-label">{{ kpi.label() }}</p>
        <p class="kpi-value">
          {{ kpi.fmt(stats[kpi.key as keyof typeof stats]) }}
        </p>
      </div>
    </div>

    <!-- Segments -->
    <div class="card">
      <div class="card-head">
        <h3 class="card-title">{{ t('customers.segments.title') }}</h3>
        <p class="card-sub">{{ t('customers.segments.subtitle') }}</p>
      </div>
      <div class="seg-list">
        <div
          v-for="(s, i) in segments"
          :key="s.name"
          class="seg-row"
          :style="{ animationDelay: `${i * 55}ms` }"
        >
          <span class="seg-dot" :style="{ background: s.color }" />
          <span class="seg-name">{{ s.name }}</span>
          <div class="seg-track">
            <div class="seg-fill" :style="{ width: s.pct + '%', background: s.color }" />
          </div>
          <span class="seg-count" :style="{ color: s.color }">{{ s.count }}</span>
        </div>
      </div>
    </div>

    <!-- Insight -->
    <div class="insight">
      <div class="insight-icon">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>
      <div>
        <p class="insight-title">{{ t('customers.insight.title') }}</p>
        <p class="insight-body">
          {{ stats.churn > 8
              ? t('customers.insight.highChurn', { count: segments.find(s => s.name === 'At Risk')?.count })
              : t('customers.insight.healthyChurn') }}
        </p>
      </div>
    </div>

  </div>
</template>

<style scoped>
.page {
  padding: 2rem;
  background: var(--bg);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header { display: flex; align-items: center; gap: .85rem; }
.header-icon {
  width: 40px; height: 40px;
  background: rgba(46,196,182,.08);
  border: 1px solid rgba(46,196,182,.18);
  border-radius: var(--r-lg);
  display: flex; align-items: center; justify-content: center;
  color: var(--teal);
  flex-shrink: 0;
}
.page-title { font-size: 1.2rem; font-weight: 600; color: var(--text); margin: 0; letter-spacing: -.01em; }
.page-sub   { font-size: .75rem; color: var(--text-muted); margin: .15rem 0 0; }

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: .85rem;
}
.kpi {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: .7rem;
  transition: border-color .2s;
}
.kpi:hover { border-color: var(--border-mid); }

.kpi-icon {
  width: 30px; height: 30px;
  background: var(--bg-hover);
  border-radius: var(--r);
  display: flex; align-items: center; justify-content: center;
  color: var(--text-sub);
}
.kpi-label { font-size: .7rem; color: var(--text-muted); margin: 0; letter-spacing: .03em; text-transform: uppercase; font-weight: 500; }
.kpi-value { font-size: 1.55rem; font-weight: 700; color: var(--text); margin: 0; letter-spacing: -.02em; font-variant-numeric: tabular-nums; }

/* Card */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}
.card-head { display: flex; flex-direction: column; gap: .15rem; }
.card-title { font-size: .88rem; font-weight: 600; color: var(--text); margin: 0; }
.card-sub   { font-size: .73rem; color: var(--text-muted); margin: 0; }

/* Segments */
.seg-list { display: flex; flex-direction: column; gap: .6rem; }
.seg-row {
  display: flex;
  align-items: center;
  gap: .8rem;
  animation: fadeIn .3s ease both;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-5px); }
  to   { opacity: 1; transform: translateX(0); }
}
.seg-dot   { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.seg-name  { font-size: .8rem; color: var(--text-sub); min-width: 110px; }
.seg-track {
  flex: 1;
  height: 5px;
  background: var(--border);
  border-radius: 99px;
  overflow: hidden;
}
.seg-fill  { height: 100%; border-radius: 99px; transition: width .7s cubic-bezier(.4,0,.2,1); opacity: .75; }
.seg-count { font-size: .78rem; font-weight: 600; font-variant-numeric: tabular-nums; min-width: 28px; text-align: right; }

/* Insight */
.insight {
  display: flex;
  align-items: flex-start;
  gap: .8rem;
  background: rgba(46,196,182,.04);
  border: 1px solid rgba(46,196,182,.15);
  border-radius: var(--r-lg);
  padding: 1.1rem 1.25rem;
}
.insight-icon {
  width: 28px; height: 28px;
  background: rgba(46,196,182,.1);
  border-radius: var(--r);
  display: flex; align-items: center; justify-content: center;
  color: var(--teal);
  flex-shrink: 0;
  margin-top: .05rem;
}
.insight-title { font-size: .78rem; font-weight: 600; color: var(--teal); margin: 0 0 .25rem; }
.insight-body  { font-size: .8rem; color: var(--text-sub); margin: 0; line-height: 1.6; }
</style>
