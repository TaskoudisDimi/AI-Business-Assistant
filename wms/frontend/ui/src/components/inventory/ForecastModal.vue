<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseModal from '@/components/ui/BaseModal.vue'
import { api } from '@/services/api'
import { intlLocale } from '@/i18n/format'

const props = defineProps<{ businessId: string; productId: string; productName: string }>()
const emit = defineEmits<{ (e: 'close'): void }>()
const { t } = useI18n()

interface Plan {
  current_stock: number; on_order: number; avg_daily: number; forecast_30: number; safety_stock: number
  suggested_qty: number; days_until_stockout: number | null; reorder_by: string | null
  lead_time_days: number; history_days: number; unit: string | null
}
const data = ref<{ history: { date: string; actual: number }[]; forecast: { date: string; forecast: number }[]; plan: Plan | null } | null>(null)
const error = ref('')

onMounted(async () => {
  try {
    const r = await api.get(`/inventory/forecast/${props.productId}`, { params: { business_id: props.businessId } })
    data.value = r.data
  } catch { error.value = t('wms.errorLoad') }
})

// One SVG: bars for the last 4 weeks, dashed line for the next 4
const chart = computed(() => {
  if (!data.value) return null
  const h = data.value.history.map(p => p.actual)
  const f = data.value.forecast.map(p => p.forecast)
  const max = Math.max(1, ...h, ...f)
  const n = h.length + f.length
  const w = 100 / n
  const bars = h.map((v, i) => ({ x: i * w + w * 0.15, w: w * 0.7, y: 100 - (v / max) * 92, hgt: (v / max) * 92 }))
  const line = f.map((v, i) => `${(h.length + i + 0.5) * w},${100 - (v / max) * 92}`).join(' ')
  return { bars, line, split: h.length * w, max }
})

const fmtDay = (iso: string | null) =>
  iso ? new Date(iso).toLocaleDateString(intlLocale(), { weekday: 'short', day: 'numeric', month: 'short' }) : '—'
</script>

<template>
  <BaseModal :title="t('forecastModal.title')" :subtitle="productName" :width="640" @close="emit('close')">
    <p v-if="error" class="ui-alert ui-alert--error">{{ error }}</p>
    <p v-else-if="!data" class="ui-muted">{{ t('common.loading') }}</p>
    <template v-else>
      <div v-if="chart" class="chart">
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
          <rect v-for="(b, i) in chart.bars" :key="i" :x="b.x" :y="b.y" :width="b.w" :height="b.hgt" fill="var(--border-mid)" />
          <line :x1="chart.split" :x2="chart.split" y1="0" y2="100" stroke="var(--border-mid)" stroke-dasharray="1.5 1.5" vector-effect="non-scaling-stroke" />
          <polyline :points="chart.line" fill="none" stroke="var(--accent)" stroke-width="2" stroke-dasharray="5 3" vector-effect="non-scaling-stroke" />
        </svg>
        <div class="legend">
          <span><i class="sw" />{{ t('forecastModal.past') }}</span>
          <span><i class="sw sw--f" />{{ t('forecastModal.next') }}</span>
        </div>
      </div>

      <div v-if="data.plan" class="stats">
        <div><span>{{ t('forecastModal.perDay') }}</span><b>{{ data.plan.avg_daily }}</b></div>
        <div><span>{{ t('forecastModal.next30') }}</span><b>{{ Math.round(data.plan.forecast_30) }}</b></div>
        <div><span>{{ t('forecastModal.runsOut') }}</span><b>{{ data.plan.days_until_stockout != null ? t('forecastModal.inDays', { n: data.plan.days_until_stockout }) : '—' }}</b></div>
        <div><span>{{ t('forecastModal.orderBy') }}</span><b>{{ fmtDay(data.plan.reorder_by) }}</b></div>
        <div><span>{{ t('forecastModal.suggested') }}</span><b>{{ data.plan.suggested_qty }} {{ data.plan.unit }}</b></div>
        <div><span>{{ t('forecastModal.safety') }}</span><b>{{ data.plan.safety_stock }}</b></div>
      </div>
      <p class="ui-hint">
        {{ data.plan && data.plan.history_days < 28 ? t('forecastModal.littleHistory') : t('forecastModal.how', { lead: data.plan?.lead_time_days ?? 7 }) }}
      </p>
    </template>
  </BaseModal>
</template>

<style scoped>
.chart svg { width: 100%; height: 160px; display: block; }
.legend { display: flex; gap: 1rem; margin-top: .4rem; font-size: .78rem; color: var(--text-muted); }
.legend span { display: inline-flex; align-items: center; gap: .35rem; }
.sw { width: 12px; height: 8px; background: var(--border-mid); display: inline-block; border-radius: 2px; }
.sw--f { height: 2px; background: var(--accent); }
.stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .5rem; }
.stats div { background: var(--bg-sunken); border-radius: var(--r); padding: .6rem .75rem; display: grid; gap: .15rem; }
.stats span { font-size: .75rem; color: var(--text-muted); }
.stats b { font-size: 1rem; font-weight: 620; font-variant-numeric: tabular-nums; }
@media (max-width: 520px) { .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
