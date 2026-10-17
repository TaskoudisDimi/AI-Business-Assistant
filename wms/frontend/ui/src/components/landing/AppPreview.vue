<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import BrandMark from '@/components/BrandMark.vue'

const { t } = useI18n()

// Static illustration of the dashboard — mirrors the real screens, not live data
const kpis = [
  { key: 'revenue', value: '€48.2k', delta: '+12%' },
  { key: 'orders',  value: '312',    delta: '+8%' },
  { key: 'low',     value: '3',      alert: true },
]
const alerts = [
  { sku: 'PW-023', name: 'Pallet wrap 23μm', days: 4 },
  { sku: 'TP-48',  name: 'Packing tape 48mm', days: 2 },
  { sku: 'GL-NIT', name: 'Nitrile gloves M',  days: 9 },
]
// Actual sales (solid) then forecast (dashed), in a 0–100 box
const actual   = '0,62 8,58 16,64 24,52 32,55 40,46 48,50 56,40'
const forecast = '56,40 64,44 72,36 80,38 88,30 100,28'
</script>

<template>
  <div class="window" role="img" :aria-label="t('landing.preview.label')">
    <div class="chrome">
      <span class="dot" /><span class="dot" /><span class="dot" />
      <span class="url">wms.task-code.com/dashboard</span>
    </div>

    <div class="app">
      <aside class="side">
        <BrandMark :size="18" />
        <span v-for="(n, i) in ['dashboard', 'inventory', 'orders', 'salesForecast']" :key="n"
          class="nav" :class="{ on: i === 0 }">{{ t(`nav.${n}`) }}</span>
      </aside>

      <div class="main">
        <div class="kpis">
          <div v-for="k in kpis" :key="k.key" class="kpi">
            <span class="kpi-l">{{ t(`landing.preview.kpi.${k.key}`) }}</span>
            <span class="kpi-v" :class="{ alert: k.alert }">{{ k.value }}</span>
            <span v-if="k.delta" class="kpi-d">{{ k.delta }}</span>
          </div>
        </div>

        <div class="row">
          <div class="card chart">
            <span class="card-t">{{ t('nav.salesForecast') }}</span>
            <svg viewBox="0 0 100 70" preserveAspectRatio="none">
              <polyline :points="actual" fill="none" stroke="var(--text-muted)" stroke-width="1.6" vector-effect="non-scaling-stroke" />
              <polyline :points="forecast" fill="none" stroke="var(--accent)" stroke-width="2" stroke-dasharray="4 3" vector-effect="non-scaling-stroke" />
              <line x1="56" y1="0" x2="56" y2="70" stroke="var(--border-mid)" stroke-dasharray="2 2" vector-effect="non-scaling-stroke" />
            </svg>
            <div class="legend">
              <span><i class="sw sw--a" />{{ t('landing.preview.actual') }}</span>
              <span><i class="sw sw--f" />{{ t('landing.preview.forecast') }}</span>
            </div>
          </div>

          <div class="card">
            <span class="card-t">{{ t('wms.inventory.ai.title') }}</span>
            <div v-for="a in alerts" :key="a.sku" class="alert-row">
              <span class="sku">{{ a.sku }}</span>
              <span class="name">{{ a.name }}</span>
              <span class="days" :class="{ crit: a.days < 7 }">{{ t('wms.inventory.ai.daysLeft', { days: a.days }) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.window {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  font-size: 12px;
  user-select: none;
}
.chrome {
  display: flex; align-items: center; gap: 6px;
  height: 34px; padding: 0 12px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-sunken);
}
.dot { width: 9px; height: 9px; border-radius: 50%; background: var(--border-mid); }
.url {
  margin-left: 10px; padding: 2px 10px; border-radius: 6px;
  background: var(--bg-card); color: var(--text-muted); font-size: 11px;
}

.app { display: grid; grid-template-columns: 150px 1fr; min-height: 300px; }
.side {
  display: flex; flex-direction: column; gap: 3px;
  padding: 12px 10px; border-right: 1px solid var(--border); background: var(--bg);
}
.side :deep(.brand) { margin: 0 0 10px 4px; }
.side :deep(.brand-name) { font-size: 12px; }
.nav { padding: 6px 8px; border-radius: 6px; color: var(--text-sub); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.nav.on { background: var(--bg-card); color: var(--text); box-shadow: inset 0 0 0 1px var(--border); }

.main { padding: 14px; display: flex; flex-direction: column; gap: 12px; background: var(--bg); }
.kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.kpi { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; display: grid; gap: 2px; }
.kpi-l { color: var(--text-muted); font-size: 11px; }
.kpi-v { font-size: 18px; font-weight: 650; letter-spacing: -.02em; }
.kpi-v.alert { color: var(--red); }
.kpi-d { color: var(--green); font-size: 11px; font-weight: 550; }

.row { display: grid; grid-template-columns: 1.2fr 1fr; gap: 10px; flex: 1; }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; display: flex; flex-direction: column; gap: 8px; min-width: 0; }
.card-t { font-weight: 600; }
.chart svg { width: 100%; height: 90px; }
.legend { display: flex; gap: 12px; color: var(--text-muted); font-size: 11px; }
.legend span { display: inline-flex; align-items: center; gap: 5px; }
.sw { width: 12px; height: 2px; display: inline-block; }
.sw--a { background: var(--text-muted); }
.sw--f { background: var(--accent); }

.alert-row { display: grid; grid-template-columns: 50px 1fr auto; gap: 8px; align-items: center; padding: 4px 0; }
.alert-row + .alert-row { border-top: 1px solid var(--border-light); }
.sku { font-family: 'Geist Mono Variable', monospace; font-size: 10.5px; color: var(--text-muted); }
.name { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.days { font-size: 11px; font-weight: 550; color: var(--amber); }
.days.crit { color: var(--red); }

@media (max-width: 640px) {
  .app { grid-template-columns: 1fr; }
  .side { display: none; }
  .row { grid-template-columns: 1fr; }
}
</style>
