<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { api } from '@/services/api'

// ─── State ────────────────────────────────────────────────────────────────────
const datasets   = ref<any[]>([])
const modelInfo  = ref<any | null>(null)
const modelError = ref(false)

const selectedId  = ref('')
const futureDays  = ref(30)
const running     = ref(false)
const result      = ref<any | null>(null)
const errorMsg    = ref<string | null>(null)
const history     = ref<any[]>([])
const activeTab   = ref<'run' | 'history'>('run')

// Extra feature overrides
const temperature    = ref('')
const promo          = ref('')
const marketingSpend = ref('')
const showExtras     = ref(false)

// Dataset compatibility check
const datasetCols  = ref<string[]>([])
const colsLoading  = ref(false)

const REQUIRED_COLS = ['date', 'sales']
const OPTIONAL_COLS = ['temperature', 'promo', 'marketing_spend']

const compatibility = computed(() => {
  if (!datasetCols.value.length) return null
  const cols = datasetCols.value.map(c => c.toLowerCase())
  const missing     = REQUIRED_COLS.filter(r => !cols.includes(r))
  const hasOptional = OPTIONAL_COLS.filter(o => cols.includes(o))
  return { missing, hasOptional, ok: missing.length === 0 }
})

const canPredict = computed(() =>
  !!selectedId.value && !modelError.value && compatibility.value?.ok === true
)

// ─── Load ─────────────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([loadDatasets(), loadModelInfo(), loadHistory()])
})

const loadDatasets = async () => {
  try {
    const r = await api.get('/datasets')
    datasets.value = r.data
    if (r.data.length) selectedId.value = r.data[0].id
  } catch {}
}

const loadModelInfo = async () => {
  try   { const r = await api.get('/predictions/model-info'); modelInfo.value = r.data }
  catch { modelError.value = true }
}

const loadHistory = async () => {
  try { const r = await api.get('/predictions'); history.value = r.data } catch {}
}

// Fetch columns whenever selected dataset changes
watch(selectedId, async (id) => {
  datasetCols.value = []
  result.value      = null
  errorMsg.value    = null
  if (!id) return
  colsLoading.value = true
  try {
    const r = await api.get(`/datasets/${id}/rows`)
    datasetCols.value = r.data.columns ?? []
  } catch {
    datasetCols.value = []
  } finally {
    colsLoading.value = false
  }
}, { immediate: true })

// ─── Predict ──────────────────────────────────────────────────────────────────
const runPrediction = async () => {
  if (!canPredict.value) return
  running.value  = true
  errorMsg.value = null
  result.value   = null
  try {
    const body: Record<string, any> = {
      dataset_id:  selectedId.value,
      future_days: futureDays.value,
    }
    if (temperature.value    !== '') body.temperature     = parseFloat(temperature.value)
    if (promo.value          !== '') body.promo           = parseFloat(promo.value)
    if (marketingSpend.value !== '') body.marketing_spend = parseFloat(marketingSpend.value)

    const r = await api.post('/predictions/run', body)
    result.value = r.data
    await loadHistory()
  } catch (e: any) {
    errorMsg.value = e.response?.data?.detail || 'Αποτυχία πρόβλεψης'
  } finally {
    running.value = false
  }
}

// ─── Chart ────────────────────────────────────────────────────────────────────
const chartPts = computed(() => {
  if (!result.value?.results?.length) return []
  const pts = result.value.results as { date: string; prediction: number }[]
  const maxV = Math.max(...pts.map(p => p.prediction))
  const minV = Math.min(...pts.map(p => p.prediction))
  const range = maxV - minV || 1
  return pts.map((p, i) => ({
    ...p,
    x: (i / (pts.length - 1)) * 100,
    y: 100 - ((p.prediction - minV) / range) * 80,
  }))
})
const polyline = computed(() => chartPts.value.map(p => `${p.x},${p.y}`).join(' '))
const area     = computed(() =>
  chartPts.value.length
    ? `0,100 ${chartPts.value.map(p => `${p.x},${p.y}`).join(' ')} 100,100`
    : ''
)

const selectedDs = computed(() => datasets.value.find(d => d.id === selectedId.value))
const fmt     = (v: number) => v?.toLocaleString('el-GR', { maximumFractionDigits: 2 }) ?? '—'
const fmtDate = (iso: string) => new Date(iso).toLocaleDateString('el-GR', { day: '2-digit', month: 'short' })
const fmtFull = (iso: string) => new Date(iso).toLocaleString('el-GR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
</script>

<template>
  <div class="sf-page">

    <!-- Header -->
    <div class="sf-header">
      <div class="sf-header-left">
        <div class="sf-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>
          </svg>
        </div>
        <div>
          <h1 class="sf-title">Sales Forecast</h1>
          <p class="sf-sub">AI πρόβλεψη μελλοντικών πωλήσεων</p>
        </div>
      </div>
      <div v-if="modelInfo"       class="mbadge mbadge--ok">  <span class="mdot"/> Μοντέλο φορτωμένο</div>
      <div v-else-if="modelError" class="mbadge mbadge--err"> ⚠ Μοντέλο δεν βρέθηκε</div>
      <div v-else                 class="mbadge mbadge--load"><span class="mini-spin"/> Φόρτωση…</div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button class="tab" :class="{ active: activeTab === 'run' }"     @click="activeTab = 'run'">▶ Πρόβλεψη</button>
      <button class="tab" :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">
        Ιστορικό <span v-if="history.length" class="tab-n">{{ history.length }}</span>
      </button>
    </div>

    <!-- ══ RUN ══ -->
    <template v-if="activeTab === 'run'">
      <div class="card">
        <div class="card-head">
          <h3 class="ctitle">Παράμετροι</h3>
          <p class="csub">Επίλεξε dataset και ορίζοντα πρόβλεψης</p>
        </div>

        <!-- Model error -->
        <div v-if="modelError" class="alert alert--warn">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          Αντίγραψε το <code>sales_model.pkl</code> στον φάκελο <code>models/</code> και επανεκκίνησε τον server.
        </div>

        <div class="cfg-grid">
          <!-- Dataset -->
          <div class="field">
            <label>Dataset</label>
            <div class="sel-wrap">
              <select v-model="selectedId" :disabled="!datasets.length">
                <option v-if="!datasets.length" value="">Δεν υπάρχουν datasets</option>
                <option v-for="d in datasets" :key="d.id" :value="d.id">{{ d.name }}</option>
              </select>
              <svg class="sel-arr" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
            </div>
            <p v-if="selectedDs" class="field-hint">{{ selectedDs.rows_count ?? '?' }} γραμμές</p>
          </div>

          <!-- Days -->
          <div class="field">
            <label>Μέρες πρόβλεψης</label>
            <div class="slider-row">
              <input type="range" v-model.number="futureDays" min="7" max="90" class="slider" />
              <span class="slider-val">{{ futureDays }}d</span>
            </div>
            <div class="presets">
              <button v-for="d in [7, 14, 30, 60, 90]" :key="d"
                class="preset" :class="{ active: futureDays === d }" @click="futureDays = d">{{ d }}</button>
            </div>
          </div>
        </div>

        <!-- ── Compatibility checker ── -->
        <div class="compat-section">
          <p class="compat-title">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            Συμβατότητα dataset
          </p>

          <div v-if="colsLoading" class="compat-row">
            <span class="mini-spin"/> <span class="compat-muted">Έλεγχος στηλών…</span>
          </div>

          <div v-else-if="!selectedId" class="compat-row">
            <span class="compat-muted">Επίλεξε dataset για έλεγχο</span>
          </div>

          <!-- ✓ Compatible -->
          <div v-else-if="compatibility?.ok" class="compat-row">
            <div class="cbadge cbadge--ok">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              Συμβατό
            </div>
            <div class="cpills">
              <span v-for="c in REQUIRED_COLS"                                                         :key="c" class="cpill cpill--ok">{{ c }}</span>
              <span v-for="c in compatibility.hasOptional"                                             :key="c" class="cpill cpill--opt">{{ c }}</span>
              <span v-for="c in OPTIONAL_COLS.filter(o => !compatibility!.hasOptional.includes(o))"   :key="c" class="cpill cpill--fwd">{{ c }} ·forward-fill</span>
            </div>
          </div>

          <!-- ✗ Incompatible -->
          <div v-else-if="compatibility && !compatibility.ok" class="cbox cbox--err">
            <div class="cbox-head">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
              Μη συμβατό dataset
            </div>
            <p class="cbox-body">Το dataset δεν έχει τις απαιτούμενες στήλες για το μοντέλο πωλήσεων.</p>

            <div class="cbox-detail">
              <div class="cdr">
                <span class="cdl cdl--miss">Λείπουν:</span>
                <span v-for="c in compatibility.missing" :key="c" class="cpill cpill--err">{{ c }}</span>
              </div>
              <div class="cdr">
                <span class="cdl">Βρέθηκαν:</span>
                <span class="cfound">{{ datasetCols.slice(0, 7).join(', ') }}{{ datasetCols.length > 7 ? ` …+${datasetCols.length - 7}` : '' }}</span>
              </div>
            </div>

            <div class="cbox-fix">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
              Ανέβασε CSV με τουλάχιστον <code>date</code> και <code>sales</code>.
              Προαιρετικά: <code>temperature</code>, <code>promo</code>, <code>marketing_spend</code>.
            </div>

            <router-link to="/datasets" class="cbox-link">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              Πήγαινε στα Datasets →
            </router-link>
          </div>
        </div>

        <!-- Extra features toggle -->
        <button class="extras-toggle" @click="showExtras = !showExtras">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
            :style="{ transform: showExtras ? 'rotate(90deg)' : 'none', transition: 'transform .2s' }">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
          Προαιρετικές παράμετροι
          <span class="ext-hint">temperature · promo · marketing_spend</span>
        </button>

        <Transition name="expand">
          <div v-if="showExtras" class="extras-grid">
            <div class="field">
              <label>Temperature</label>
              <input v-model="temperature" type="number" step="0.1" placeholder="Αυτόματο (forward-fill)" />
            </div>
            <div class="field">
              <label>Promo (0 / 1)</label>
              <div class="sel-wrap">
                <select v-model="promo">
                  <option value="">Αυτόματο</option>
                  <option value="0">0 — Χωρίς promo</option>
                  <option value="1">1 — Με promo</option>
                </select>
                <svg class="sel-arr" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
              </div>
            </div>
            <div class="field">
              <label>Marketing Spend</label>
              <input v-model="marketingSpend" type="number" step="1" placeholder="Αυτόματο (forward-fill)" />
            </div>
          </div>
        </Transition>

        <!-- Predict button -->
        <button
          class="btn-predict"
          :disabled="running || !canPredict"
          :title="!canPredict && compatibility && !compatibility.ok
            ? 'Το dataset χρειάζεται στήλες date και sales'
            : undefined"
          @click="runPrediction"
        >
          <span v-if="running" class="mini-spin white"/>
          <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          {{ running ? 'Εκτέλεση…' : 'Εκτέλεση Predict' }}
        </button>

        <Transition name="msg">
          <div v-if="errorMsg" class="alert alert--err" @click="errorMsg = null">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {{ errorMsg }}
          </div>
        </Transition>
      </div>

      <!-- Results -->
      <Transition name="results-in">
        <div v-if="result" class="results">
          <div class="kpi-row">
            <div class="kpi"><p class="kpi-l">Σύνολο {{ result.future_days }}d</p><p class="kpi-v blue">{{ fmt(result.summary.total) }}</p></div>
            <div class="kpi"><p class="kpi-l">Μέσος / ημέρα</p><p class="kpi-v">{{ fmt(result.summary.avg) }}</p></div>
            <div class="kpi"><p class="kpi-l">Peak</p><p class="kpi-v green">{{ fmtDate(result.summary.peak_date) }}</p></div>
            <div class="kpi"><p class="kpi-l">Εύρος</p><p class="kpi-v">{{ fmt(result.summary.min) }}–{{ fmt(result.summary.max) }}</p></div>
          </div>

          <div class="card">
            <div class="card-head">
              <h3 class="ctitle">Πρόβλεψη — επόμενες {{ result.future_days }} ημέρες</h3>
              <p class="csub">{{ result.dataset_name }}</p>
            </div>
            <div class="chart-wrap">
              <svg viewBox="0 0 100 100" preserveAspectRatio="none" class="chart-svg">
                <defs>
                  <linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%"   stop-color="#4a9eff" stop-opacity=".28"/>
                    <stop offset="100%" stop-color="#4a9eff" stop-opacity="0"/>
                  </linearGradient>
                </defs>
                <polygon  :points="area"     fill="url(#ag)"/>
                <polyline :points="polyline" fill="none" stroke="#4a9eff" stroke-width=".55" stroke-linejoin="round"/>
                <circle
                  v-for="(p, i) in chartPts.filter((_, i) => i % 7 === 0 || i === chartPts.length - 1)"
                  :key="i" :cx="p.x" :cy="p.y" r="1.1" fill="#4a9eff"
                />
              </svg>
              <div class="x-labels">
                <span v-for="(p, i) in chartPts.filter((_, i) => i % Math.ceil(chartPts.length / 5) === 0)" :key="i" class="x-lbl">
                  {{ fmtDate(p.date) }}
                </span>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-head">
              <h3 class="ctitle">Αναλυτικά</h3>
              <p class="csub">Πρώτες 10 από {{ result.results.length }} ημέρες</p>
            </div>
            <div class="tbl-wrap">
              <table class="ptbl">
                <thead><tr><th>#</th><th>Ημερομηνία</th><th>Πρόβλεψη</th><th></th></tr></thead>
                <tbody>
                  <tr v-for="(row, i) in result.results.slice(0, 10)" :key="i">
                    <td class="td-n">{{ Number(i) + 1 }}</td>
                    <td class="td-d">{{ fmtDate(row.date) }}</td>
                    <td class="td-p">{{ fmt(row.prediction) }}</td>
                    <td><div class="bar"><div class="bar-f" :style="{ width: `${(row.prediction / result.summary.max * 100).toFixed(1)}%` }"/></div></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </Transition>
    </template>

    <!-- ══ HISTORY ══ -->
    <template v-else>
      <div class="card">
        <div v-if="!history.length" class="empty">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          <p>Δεν υπάρχει ιστορικό ακόμα</p>
        </div>
        <div v-else class="hist-list">
          <div v-for="h in history" :key="h.id" class="hist-item">
            <div class="hist-icon"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/></svg></div>
            <div class="hist-info">
              <p class="hist-type">Sales Forecast</p>
              <p class="hist-date">{{ fmtFull(h.created_at) }}</p>
            </div>
            <span v-if="h.result?.summary?.total" class="hist-tag">{{ fmt(h.result.summary.total) }} total</span>
          </div>
        </div>
      </div>
    </template>

  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@400;500;600;700&display=swap');

.sf-page { min-height:100vh; padding:2rem 2.5rem; background:#080d16; font-family:'Sora',sans-serif; color:#c8d6e8; display:flex; flex-direction:column; gap:1.5rem; }

.sf-header { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem; }
.sf-header-left { display:flex; align-items:center; gap:1rem; }
.sf-icon { width:44px;height:44px;background:linear-gradient(135deg,#1a2640,#0e1a2e);border:1px solid #1e3050;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#4a9eff; }
.sf-title { font-size:1.4rem;font-weight:700;color:#e8f0fe;margin:0;letter-spacing:-.02em; }
.sf-sub   { font-size:.78rem;color:#3d5570;margin:.1rem 0 0;font-family:'DM Mono',monospace; }

.mbadge { display:flex;align-items:center;gap:.45rem;font-size:.7rem;font-weight:600;padding:.28rem .8rem;border-radius:999px;font-family:'DM Mono',monospace;border:1px solid; }
.mbadge--ok   { background:#0d2a1a;border-color:#1a4a30;color:#3a9a60; }
.mbadge--err  { background:#1f0a0a;border-color:#3d1515;color:#cc5050; }
.mbadge--load { background:#0a1525;border-color:#162035;color:#3a6080; }
.mdot { width:6px;height:6px;background:#3a9a60;border-radius:50%;box-shadow:0 0 8px #3a9a60;animation:pdot 2s ease infinite; }
@keyframes pdot{0%,100%{opacity:1}50%{opacity:.3}}

.tabs { display:flex;gap:.3rem; }
.tab { display:flex;align-items:center;gap:.45rem;background:#0a1220;border:1px solid #111e33;color:#3a5a80;border-radius:10px;padding:.5rem 1rem;font-size:.8rem;font-weight:500;font-family:'Sora',sans-serif;cursor:pointer;transition:all .15s; }
.tab.active { background:#0d2040;border-color:#1a3460;color:#7ab8ff; }
.tab:hover:not(.active){ background:#0d1f38;color:#7ab0e0; }
.tab-n { background:#1a3460;color:#7ab8ff;font-size:.65rem;padding:.1rem .4rem;border-radius:999px;font-family:'DM Mono',monospace; }

.card { background:#0a1220;border:1px solid #111e33;border-radius:14px;padding:1.5rem;display:flex;flex-direction:column;gap:1.1rem; }
.card-head { display:flex;flex-direction:column;gap:.2rem; }
.ctitle { font-size:.9rem;font-weight:700;color:#b8d0ec;margin:0; }
.csub   { font-size:.75rem;color:#2a4060;margin:0; }

.cfg-grid { display:grid;grid-template-columns:1fr 1fr;gap:1rem; }
@media(max-width:600px){.cfg-grid{grid-template-columns:1fr;}}
.field { display:flex;flex-direction:column;gap:.4rem; }
.field-hint { font-size:.7rem;color:#1e3a5a;font-family:'DM Mono',monospace;margin:0; }
label { font-size:.68rem;font-weight:600;color:#2a4060;letter-spacing:.06em;text-transform:uppercase;font-family:'DM Mono',monospace; }
input,select { background:#080d16;border:1px solid #111e33;border-radius:9px;color:#c8d6e8;padding:.6rem .85rem;font-size:.83rem;font-family:'Sora',sans-serif;outline:none;width:100%;box-sizing:border-box;appearance:none;transition:border-color .15s; }
input:focus,select:focus { border-color:#2a5299;box-shadow:0 0 0 3px #2a529920; }
input::placeholder { color:#1e3a5a; }
.sel-wrap { position:relative; }
.sel-arr { position:absolute;right:.8rem;top:50%;transform:translateY(-50%);color:#2a4060;pointer-events:none; }

.slider-row { display:flex;align-items:center;gap:.75rem; }
.slider { flex:1;height:4px;padding:0;background:linear-gradient(90deg,#2a5299 0%,#111e33 0%);border-radius:99px;cursor:pointer; }
.slider::-webkit-slider-thumb { appearance:none;width:16px;height:16px;background:#4a9eff;border-radius:50%;cursor:pointer;box-shadow:0 0 0 3px #4a9eff33; }
.slider-val { font-size:.78rem;color:#4a9eff;font-family:'DM Mono',monospace;white-space:nowrap; }
.presets { display:flex;gap:.35rem; }
.preset { background:#0e1f38;border:1px solid #162a48;color:#3a6080;border-radius:7px;padding:.22rem .55rem;font-size:.7rem;font-family:'DM Mono',monospace;cursor:pointer;transition:all .15s; }
.preset.active { background:#1a3460;border-color:#2a4a7a;color:#7ab8ff; }
.preset:hover:not(.active){ border-color:#2a4060;color:#5a8acc; }

/* ── Compatibility ── */
.compat-section { display:flex;flex-direction:column;gap:.6rem; }
.compat-title { display:flex;align-items:center;gap:.4rem;font-size:.68rem;font-weight:600;color:#2a4060;letter-spacing:.06em;text-transform:uppercase;font-family:'DM Mono',monospace;margin:0; }
.compat-row { display:flex;align-items:center;gap:.65rem;flex-wrap:wrap; }
.compat-muted { font-size:.8rem;color:#1e3050; }
.cbadge { display:inline-flex;align-items:center;gap:.35rem;font-size:.7rem;font-weight:600;padding:.2rem .65rem;border-radius:999px;font-family:'DM Mono',monospace; }
.cbadge--ok { background:#0d2a1a;border:1px solid #1a4a30;color:#3a9a60; }
.cpills { display:flex;flex-wrap:wrap;gap:.3rem; }
.cpill { font-size:.67rem;font-family:'DM Mono',monospace;padding:.15rem .5rem;border-radius:6px;border:1px solid; }
.cpill--ok  { background:#0d2a1a;border-color:#1a4a30;color:#3a9a60; }
.cpill--opt { background:#0a1a2a;border-color:#1a3050;color:#4a9eff; }
.cpill--fwd { background:#0a1220;border-color:#111e33;color:#2a4060; }
.cpill--err { background:#1f0a0a;border-color:#3d1515;color:#f07070; }

.cbox { border-radius:12px;padding:1.1rem;display:flex;flex-direction:column;gap:.7rem; }
.cbox--err { background:#120808;border:1px solid #2a1010; }
.cbox-head { display:flex;align-items:center;gap:.55rem;font-size:.85rem;font-weight:700;color:#cc5050; }
.cbox-body { font-size:.8rem;color:#7a3a3a;margin:0;line-height:1.5; }
.cbox-detail { display:flex;flex-direction:column;gap:.4rem;background:#0a0606;border:1px solid #1e0e0e;border-radius:8px;padding:.75rem; }
.cdr { display:flex;align-items:center;gap:.5rem;flex-wrap:wrap; }
.cdl { font-size:.67rem;font-weight:600;font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:.05em;color:#4a2a2a;min-width:64px; }
.cdl--miss { color:#cc5050; }
.cfound { font-size:.74rem;color:#4a3030;font-family:'DM Mono',monospace; }
.cbox-fix { display:flex;align-items:flex-start;gap:.5rem;font-size:.78rem;color:#6a4040;line-height:1.5; }
.cbox-fix code { background:#1a0808;color:#cc7070;padding:.1rem .35rem;border-radius:4px;font-family:'DM Mono',monospace;font-size:.74rem; }
.cbox-link { display:inline-flex;align-items:center;gap:.45rem;background:#1a0a0a;border:1px solid #3d1515;color:#cc5050;border-radius:8px;padding:.38rem .75rem;font-size:.77rem;font-weight:600;text-decoration:none;transition:background .15s;align-self:flex-start; }
.cbox-link:hover { background:#2a1010; }

.alert { display:flex;align-items:flex-start;gap:.6rem;border-radius:10px;padding:.75rem 1rem;font-size:.8rem; }
.alert--warn { background:#1a1500;border:1px solid #3a3000;color:#c0a020; }
.alert--warn code { background:#0e1000;padding:.1rem .35rem;border-radius:4px;font-family:'DM Mono',monospace; }
.alert--err { background:#1f0a0a;border:1px solid #3d1515;color:#f07070;cursor:pointer; }

.extras-toggle { display:flex;align-items:center;gap:.5rem;background:transparent;border:1px dashed #111e33;color:#2a4060;border-radius:9px;padding:.5rem .85rem;font-size:.78rem;font-family:'Sora',sans-serif;cursor:pointer;transition:border-color .15s,color .15s;align-self:flex-start; }
.extras-toggle:hover { border-color:#1a3460;color:#4a7acc; }
.ext-hint { font-size:.67rem;font-family:'DM Mono',monospace;opacity:.55; }
.extras-grid { display:grid;grid-template-columns:1fr 1fr 1fr;gap:.85rem; }
@media(max-width:600px){.extras-grid{grid-template-columns:1fr;}}

.btn-predict { display:inline-flex;align-items:center;gap:.5rem;background:linear-gradient(135deg,#1a3a6a,#1a2a58);border:1px solid #2a4a8a;color:#7ab8ff;border-radius:10px;padding:.7rem 1.4rem;font-size:.88rem;font-weight:600;font-family:'Sora',sans-serif;cursor:pointer;align-self:flex-start;transition:background .15s,box-shadow .15s;box-shadow:0 4px 20px rgba(74,158,255,.15); }
.btn-predict:hover:not(:disabled) { background:linear-gradient(135deg,#22448a,#1a3468);box-shadow:0 4px 24px rgba(74,158,255,.3); }
.btn-predict:disabled { opacity:.35;cursor:not-allowed;box-shadow:none; }

.results { display:flex;flex-direction:column;gap:1rem; }
.kpi-row { display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:.75rem; }
.kpi { background:#0a1220;border:1px solid #111e33;border-radius:12px;padding:1rem; }
.kpi-l { font-size:.68rem;color:#2a4060;margin:0 0 .3rem;font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:.04em; }
.kpi-v { font-size:1.05rem;font-weight:700;color:#b8d0ec;margin:0;font-family:'DM Mono',monospace; }
.kpi-v.blue { color:#4a9eff; } .kpi-v.green { color:#3a9a60; }

.chart-wrap { display:flex;flex-direction:column;gap:.5rem; }
.chart-svg  { width:100%;height:160px;display:block;overflow:visible; }
.x-labels   { display:flex;justify-content:space-between; }
.x-lbl      { font-size:.62rem;color:#2a4060;font-family:'DM Mono',monospace; }

.tbl-wrap { overflow-x:auto; }
.ptbl { width:100%;border-collapse:collapse;font-size:.82rem; }
.ptbl th { padding:.6rem 1rem;text-align:left;font-size:.67rem;font-weight:600;letter-spacing:.07em;text-transform:uppercase;color:#2a4060;font-family:'DM Mono',monospace;border-bottom:1px solid #111e33; }
.ptbl tr { border-bottom:1px solid #0d1828;transition:background .1s; }
.ptbl tr:hover { background:#0e1f38; }
.ptbl td { padding:.5rem 1rem;vertical-align:middle; }
.td-n { color:#1e3a5a;font-family:'DM Mono',monospace; }
.td-d { color:#7a9cc0;font-family:'DM Mono',monospace;font-size:.8rem; }
.td-p { font-weight:600;color:#a0c8f0;font-family:'DM Mono',monospace; }
.bar  { height:5px;background:#111e33;border-radius:99px;overflow:hidden;width:80px; }
.bar-f { height:100%;background:linear-gradient(90deg,#1a3460,#4a9eff);border-radius:99px;transition:width .5s ease; }

.empty { display:flex;flex-direction:column;align-items:center;padding:3rem;gap:.75rem;color:#1e3050;font-size:.85rem; }
.hist-list { display:flex;flex-direction:column;gap:.45rem; }
.hist-item { display:flex;align-items:center;gap:.85rem;background:#080d16;border:1px solid #0e1e33;border-radius:10px;padding:.8rem 1rem;transition:background .12s; }
.hist-item:hover { background:#0d1f38; }
.hist-icon { width:30px;height:30px;background:#0e1f38;border:1px solid #162a48;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#3a6fcc; }
.hist-type { font-size:.82rem;font-weight:600;color:#8ab4d8;margin:0; }
.hist-date { font-size:.68rem;color:#2a4060;margin:.1rem 0 0;font-family:'DM Mono',monospace; }
.hist-tag  { margin-left:auto;background:#0d2040;border:1px solid #1a3460;color:#5a8acc;font-size:.68rem;padding:.18rem .5rem;border-radius:999px;font-family:'DM Mono',monospace; }

.mini-spin { width:12px;height:12px;border-radius:50%;border:2px solid transparent;border-top-color:currentColor;animation:spin .6s linear infinite;display:inline-block; }
.mini-spin.white { border-top-color:white; }
@keyframes spin{to{transform:rotate(360deg)}}

.expand-enter-active  { transition:all .25s ease; }
.expand-leave-active  { transition:all .15s ease; }
.expand-enter-from, .expand-leave-to { opacity:0;transform:translateY(-6px); }
.msg-enter-active { transition:all .2s ease; } .msg-leave-active { transition:all .15s ease; }
.msg-enter-from, .msg-leave-to { opacity:0;transform:translateY(-4px); }
.results-in-enter-active { transition:all .3s ease; }
.results-in-enter-from   { opacity:0;transform:translateY(10px); }
</style>