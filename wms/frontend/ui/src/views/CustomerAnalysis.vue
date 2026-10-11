<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { api } from '@/services/api'

const auth = useAuthStore()
const { t } = useI18n()

interface Customer {
  name: string
  total_orders: number
  total_revenue: number
  avg_order_value: number
  days_since_last_order: number
  last_order_date: string
  first_order_date: string
  segment: 'high_value' | 'loyal' | 'at_risk' | 'new' | 'dormant'
}

interface TopProduct {
  sku: string
  name: string
  total_qty: number
  total_revenue: number
}

interface AnalysisData {
  summary: { total_customers: number; total_revenue: number; avg_order_value: number; at_risk_count: number }
  customers: Customer[]
  segments: Record<string, number>
  top_products: TopProduct[]
}

const data    = ref<AnalysisData | null>(null)
const loading = ref(true)
const error   = ref('')
const sortKey = ref<keyof Customer>('total_revenue')
const sortAsc = ref(false)
const search  = ref('')

const businessId = computed(() => auth.currentBusiness?.id ?? '')

async function load() {
  if (!businessId.value) { loading.value = false; return }
  loading.value = true; error.value = ''
  try {
    const r = await api.get('/customers/analysis', { params: { business_id: businessId.value } })
    data.value = r.data
  } catch { error.value = 'Failed to load customer data' }
  finally { loading.value = false }
}

onMounted(load)

const filteredCustomers = computed(() => {
  if (!data.value) return []
  let list = data.value.customers
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(c => c.name.toLowerCase().includes(q))
  }
  return [...list].sort((a, b) => {
    const av = a[sortKey.value] as number | string
    const bv = b[sortKey.value] as number | string
    const cmp = av < bv ? -1 : av > bv ? 1 : 0
    return sortAsc.value ? cmp : -cmp
  })
})

function setSort(key: keyof Customer) {
  if (sortKey.value === key) sortAsc.value = !sortAsc.value
  else { sortKey.value = key; sortAsc.value = false }
}

const totalCustomers = computed(() => data.value?.summary.total_customers ?? 0)

const segmentColors: Record<string, string> = {
  high_value: 'var(--teal)',
  loyal:      '#34d399',
  at_risk:    'var(--amber)',
  new:        '#a78bfa',
  dormant:    'var(--red)',
}

const segmentList = computed(() => {
  if (!data.value) return []
  return Object.entries(data.value.segments)
    .filter(([, count]) => count > 0)
    .map(([key, count]) => ({
      key,
      label: t(`customers.segments.${key}`),
      count,
      pct: Math.round((count / Math.max(totalCustomers.value, 1)) * 100),
      color: segmentColors[key] ?? 'var(--text-muted)',
    }))
    .sort((a, b) => b.count - a.count)
})

function fmt(n: number) { return n.toLocaleString('el-GR', { minimumFractionDigits: 0, maximumFractionDigits: 2 }) }

const insightText = computed(() => {
  if (!data.value) return ''
  if (data.value.summary.total_customers === 0) return t('customers.insight.noOrders')
  if (data.value.summary.at_risk_count > 0)
    return t('customers.insight.atRisk', { count: data.value.summary.at_risk_count })
  return t('customers.insight.healthy')
})
</script>

<template>
  <div class="page">

    <!-- Header -->
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

    <!-- Loading / Error -->
    <div v-if="loading" class="state-msg">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="state-msg state-msg--error">{{ error }}</div>

    <!-- No data empty state -->
    <template v-else-if="data && data.summary.total_customers === 0">
      <div class="empty-state">
        <div class="empty-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
          </svg>
        </div>
        <p class="empty-title">{{ t('customers.noData.title') }}</p>
        <p class="empty-hint">{{ t('customers.noData.hint') }}</p>
      </div>
    </template>

    <!-- Data -->
    <template v-else-if="data">

      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi">
          <div class="kpi-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 00-3-3.87"/>
              <path d="M16 3.13a4 4 0 010 7.75"/>
            </svg>
          </div>
          <p class="kpi-label">{{ t('customers.kpi.total') }}</p>
          <p class="kpi-value">{{ data.summary.total_customers }}</p>
        </div>

        <div class="kpi">
          <div class="kpi-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <line x1="12" y1="1" x2="12" y2="23"/>
              <path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
            </svg>
          </div>
          <p class="kpi-label">{{ t('customers.kpi.revenue') }}</p>
          <p class="kpi-value">€{{ fmt(data.summary.total_revenue) }}</p>
        </div>

        <div class="kpi">
          <div class="kpi-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <path d="M16 10a4 4 0 01-8 0"/>
            </svg>
          </div>
          <p class="kpi-label">{{ t('customers.kpi.avgOrder') }}</p>
          <p class="kpi-value">€{{ fmt(data.summary.avg_order_value) }}</p>
        </div>

        <div class="kpi kpi--alert" :class="{ 'kpi--warn': data.summary.at_risk_count > 0 }">
          <div class="kpi-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <p class="kpi-label">{{ t('customers.kpi.atRisk') }}</p>
          <p class="kpi-value">{{ data.summary.at_risk_count }}</p>
        </div>
      </div>

      <!-- Middle row: Segments + Top Products -->
      <div class="mid-row">

        <!-- RFM Segments -->
        <div class="card">
          <div class="card-head">
            <h3 class="card-title">{{ t('customers.segments.title') }}</h3>
            <p class="card-sub">{{ t('customers.segments.subtitle') }}</p>
          </div>
          <div class="seg-list">
            <div v-for="s in segmentList" :key="s.key" class="seg-row">
              <span class="seg-dot" :style="{ background: s.color }" />
              <span class="seg-name">{{ s.label }}</span>
              <div class="seg-track">
                <div class="seg-fill" :style="{ width: s.pct + '%', background: s.color }" />
              </div>
              <span class="seg-count" :style="{ color: s.color }">{{ s.count }}</span>
            </div>
          </div>
        </div>

        <!-- Top Products -->
        <div class="card">
          <div class="card-head">
            <h3 class="card-title">{{ t('customers.products.title') }}</h3>
            <p class="card-sub">{{ t('customers.products.subtitle') }}</p>
          </div>
          <div v-if="data.top_products.length === 0" class="card-empty">—</div>
          <div v-else class="prod-list">
            <div v-for="(p, i) in data.top_products" :key="p.sku" class="prod-row">
              <span class="prod-rank">{{ i + 1 }}</span>
              <div class="prod-info">
                <span class="prod-sku">{{ p.sku }}</span>
                <span class="prod-name">{{ p.name }}</span>
              </div>
              <div class="prod-stats">
                <span class="prod-qty">{{ p.total_qty }} pcs</span>
                <span class="prod-rev">€{{ fmt(p.total_revenue) }}</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Customer Leaderboard -->
      <div class="card">
        <div class="card-head-row">
          <div>
            <h3 class="card-title">{{ t('customers.table.title') }}</h3>
            <p class="card-sub">{{ t('customers.table.subtitle') }}</p>
          </div>
          <div class="search-wrap">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input v-model="search" class="search-input" placeholder="Search…" />
          </div>
        </div>
        <div class="tbl-wrap">
          <table class="tbl">
            <thead>
              <tr>
                <th class="sortable" @click="setSort('name')">
                  {{ t('customers.table.customer') }}
                  <span class="sort-arrow" v-if="sortKey === 'name'">{{ sortAsc ? '↑' : '↓' }}</span>
                </th>
                <th class="num sortable" @click="setSort('total_orders')">
                  {{ t('customers.table.orders') }}
                  <span class="sort-arrow" v-if="sortKey === 'total_orders'">{{ sortAsc ? '↑' : '↓' }}</span>
                </th>
                <th class="num sortable" @click="setSort('total_revenue')">
                  {{ t('customers.table.revenue') }}
                  <span class="sort-arrow" v-if="sortKey === 'total_revenue'">{{ sortAsc ? '↑' : '↓' }}</span>
                </th>
                <th class="num sortable" @click="setSort('avg_order_value')">
                  {{ t('customers.table.avgOrder') }}
                  <span class="sort-arrow" v-if="sortKey === 'avg_order_value'">{{ sortAsc ? '↑' : '↓' }}</span>
                </th>
                <th class="num sortable" @click="setSort('days_since_last_order')">
                  {{ t('customers.table.lastOrder') }}
                  <span class="sort-arrow" v-if="sortKey === 'days_since_last_order'">{{ sortAsc ? '↑' : '↓' }}</span>
                </th>
                <th>{{ t('customers.table.segment') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in filteredCustomers" :key="c.name">
                <td class="fw">{{ c.name }}</td>
                <td class="num">{{ c.total_orders }}</td>
                <td class="num fw">€{{ fmt(c.total_revenue) }}</td>
                <td class="num muted">€{{ fmt(c.avg_order_value) }}</td>
                <td class="num">
                  <span :class="['days-badge', c.days_since_last_order > 60 ? 'days--warn' : c.days_since_last_order > 30 ? 'days--mid' : 'days--ok']">
                    {{ c.days_since_last_order }}d ago
                  </span>
                </td>
                <td>
                  <span class="seg-badge" :style="{ color: segmentColors[c.segment], borderColor: segmentColors[c.segment] + '44', background: segmentColors[c.segment] + '14' }">
                    {{ t(`customers.segments.${c.segment}`) }}
                  </span>
                </td>
              </tr>
              <tr v-if="filteredCustomers.length === 0">
                <td colspan="6" class="tbl-empty">{{ t('common.noData') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- AI Insight -->
      <div class="insight">
        <div class="insight-icon">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        </div>
        <div>
          <p class="insight-title">{{ t('customers.insight.title') }}</p>
          <p class="insight-body">{{ insightText }}</p>
        </div>
      </div>

    </template>
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
  background: rgba(62,207,191,.08); border: 1px solid rgba(62,207,191,.18);
  border-radius: var(--r-lg); display: flex; align-items: center; justify-content: center;
  color: var(--teal); flex-shrink: 0;
}
.page-title { font-size: 1.2rem; font-weight: 600; color: var(--text); margin: 0; letter-spacing: -.01em; }
.page-sub   { font-size: .75rem; color: var(--text-muted); margin: .15rem 0 0; }

.state-msg { font-size: .82rem; color: var(--text-muted); padding: 2rem; text-align: center; }
.state-msg--error { color: var(--red); }

.empty-state {
  display: flex; flex-direction: column; align-items: center; gap: .75rem; padding: 3rem 1rem;
}
.empty-icon {
  width: 52px; height: 52px; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--r-xl); display: flex; align-items: center; justify-content: center;
  color: var(--text-muted);
}
.empty-title { font-size: .95rem; font-weight: 600; color: var(--text); margin: 0; }
.empty-hint  { font-size: .78rem; color: var(--text-muted); margin: 0; }

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: .85rem;
}
.kpi {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: 1.2rem;
  display: flex; flex-direction: column; gap: .6rem;
  transition: border-color .2s;
}
.kpi:hover { border-color: var(--border-mid); }
.kpi--warn { border-color: rgba(224,85,85,.3) !important; background: rgba(224,85,85,.04); }

.kpi-icon {
  width: 30px; height: 30px; background: var(--bg-hover); border-radius: var(--r);
  display: flex; align-items: center; justify-content: center; color: var(--text-sub);
}
.kpi--warn .kpi-icon { color: var(--red); background: var(--red-bg); }
.kpi-label { font-size: .68rem; color: var(--text-muted); margin: 0; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; }
.kpi-value { font-size: 1.55rem; font-weight: 700; color: var(--text); margin: 0; letter-spacing: -.02em; font-variant-numeric: tabular-nums; }
.kpi--warn .kpi-value { color: var(--red); }

/* Mid Row */
.mid-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
@media (max-width: 700px) { .mid-row { grid-template-columns: 1fr; } }

/* Card */
.card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: 1.25rem;
  display: flex; flex-direction: column; gap: 1rem;
}
.card-head { display: flex; flex-direction: column; gap: .12rem; }
.card-head-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.card-title { font-size: .88rem; font-weight: 600; color: var(--text); margin: 0; }
.card-sub   { font-size: .72rem; color: var(--text-muted); margin: 0; }
.card-empty { font-size: .8rem; color: var(--text-muted); text-align: center; padding: 1rem 0; }

/* Segments */
.seg-list { display: flex; flex-direction: column; gap: .55rem; }
.seg-row  { display: flex; align-items: center; gap: .7rem; }
.seg-dot  { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.seg-name { font-size: .78rem; color: var(--text-sub); min-width: 100px; }
.seg-track {
  flex: 1; height: 5px; background: var(--border); border-radius: 99px; overflow: hidden;
}
.seg-fill  { height: 100%; border-radius: 99px; transition: width .7s cubic-bezier(.4,0,.2,1); opacity: .75; }
.seg-count { font-size: .78rem; font-weight: 600; font-variant-numeric: tabular-nums; min-width: 22px; text-align: right; }

/* Top Products */
.prod-list { display: flex; flex-direction: column; gap: .45rem; }
.prod-row  {
  display: flex; align-items: center; gap: .75rem;
  padding: .4rem .5rem; border-radius: var(--r); transition: background .12s;
}
.prod-row:hover { background: var(--bg-hover); }
.prod-rank { font-size: .7rem; font-weight: 700; color: var(--text-muted); width: 16px; text-align: center; flex-shrink: 0; }
.prod-info { display: flex; align-items: center; gap: .45rem; flex: 1; min-width: 0; }
.prod-sku  { font-size: .68rem; color: var(--teal); font-family: monospace; font-weight: 600; flex-shrink: 0; }
.prod-name { font-size: .78rem; color: var(--text-sub); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.prod-stats { display: flex; align-items: center; gap: .6rem; flex-shrink: 0; }
.prod-qty  { font-size: .72rem; color: var(--text-muted); }
.prod-rev  { font-size: .78rem; font-weight: 600; color: var(--text); font-variant-numeric: tabular-nums; }

/* Search */
.search-wrap {
  display: flex; align-items: center; gap: .4rem;
  background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--r); padding: .3rem .65rem;
  color: var(--text-muted);
}
.search-input {
  background: transparent; border: none; outline: none;
  color: var(--text); font-size: .78rem; width: 140px;
}
.search-input::placeholder { color: var(--text-muted); }

/* Table */
.tbl-wrap { overflow-x: auto; margin: -.25rem -1.25rem 0; }
.tbl { width: 100%; border-collapse: collapse; font-size: .8rem; }
.tbl thead { background: var(--bg); border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); }
.tbl th {
  padding: .6rem 1.25rem; font-size: .65rem; font-weight: 600;
  color: var(--text-muted); letter-spacing: .06em; text-transform: uppercase;
  text-align: left; white-space: nowrap; user-select: none;
}
.tbl th.num { text-align: right; }
.tbl th.sortable { cursor: pointer; }
.tbl th.sortable:hover { color: var(--text-sub); }
.sort-arrow { margin-left: .25rem; opacity: .7; }

.tbl td { padding: .72rem 1.25rem; color: var(--text-sub); border-bottom: 1px solid var(--border); }
.tbl tbody tr:last-child td { border-bottom: none; }
.tbl tbody tr:hover { background: var(--bg-hover); }
.tbl td.num  { text-align: right; font-variant-numeric: tabular-nums; }
.tbl td.fw   { color: var(--text); font-weight: 500; }
.tbl td.muted { color: var(--text-muted); }
.tbl-empty   { text-align: center; color: var(--text-muted); font-style: italic; padding: 1.5rem; }

.days-badge {
  display: inline-block; font-size: .7rem; font-weight: 600;
  padding: .1rem .4rem; border-radius: var(--r);
}
.days--ok   { background: var(--green-bg); color: var(--green); }
.days--mid  { background: rgba(212,160,23,.1); color: var(--amber); }
.days--warn { background: var(--red-bg); color: var(--red); }

.seg-badge {
  display: inline-block; font-size: .68rem; font-weight: 600;
  padding: .1rem .45rem; border-radius: var(--r);
  border-width: 1px; border-style: solid; letter-spacing: .02em;
}

/* Insight */
.insight {
  display: flex; align-items: flex-start; gap: .8rem;
  background: rgba(62,207,191,.04); border: 1px solid rgba(62,207,191,.15);
  border-radius: var(--r-lg); padding: 1.1rem 1.25rem;
}
.insight-icon {
  width: 28px; height: 28px; background: rgba(62,207,191,.1);
  border-radius: var(--r); display: flex; align-items: center; justify-content: center;
  color: var(--teal); flex-shrink: 0; margin-top: .05rem;
}
.insight-title { font-size: .78rem; font-weight: 600; color: var(--teal); margin: 0 0 .25rem; }
.insight-body  { font-size: .8rem; color: var(--text-sub); margin: 0; line-height: 1.6; }
</style>
