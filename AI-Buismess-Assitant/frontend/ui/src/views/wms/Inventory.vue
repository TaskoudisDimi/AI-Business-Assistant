<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { api } from '@/services/api'

const auth = useAuthStore()
const { t } = useI18n()

interface InvItem {
  id: string
  quantity: number
  last_updated: string
  products: {
    id: string; sku: string; name: string
    category: string | null; unit: string; reorder_point: number
  }
}

interface Suggestion {
  product_id: string; sku: string; name: string
  category: string | null; unit: string | null
  current_stock: number; reorder_point: number
  avg_daily_outbound: number; days_until_stockout: number | null
  urgency: 'critical' | 'warning'
}

const items       = ref<InvItem[]>([])
const suggestions = ref<Suggestion[]>([])
const loading     = ref(true)
const error       = ref('')
const showMovementModal = ref(false)
const movTarget   = ref<InvItem | null>(null)
const saving      = ref(false)

const movForm = ref({
  type: 'inbound' as 'inbound' | 'outbound' | 'adjustment',
  quantity: 1,
  reason: '',
})

const businessId = computed(() => auth.currentBusiness?.id ?? '')

async function load() {
  if (!businessId.value) { loading.value = false; return }
  loading.value = true; error.value = ''
  try {
    const [invRes, sugRes] = await Promise.allSettled([
      api.get('/inventory', { params: { business_id: businessId.value } }),
      api.get('/inventory/reorder-suggestions', { params: { business_id: businessId.value } }),
    ])
    items.value = invRes.status === 'fulfilled' ? invRes.value.data : []
    suggestions.value = sugRes.status === 'fulfilled' ? sugRes.value.data : []
  } catch { error.value = t('wms.errorLoad') }
  finally { loading.value = false }
}

onMounted(load)

function openMovement(item: InvItem) {
  movTarget.value = item
  movForm.value = { type: 'inbound', quantity: 1, reason: '' }
  showMovementModal.value = true
}

async function saveMovement() {
  if (!movTarget.value || !businessId.value) return
  saving.value = true
  try {
    await api.post('/inventory/movement', {
      business_id: businessId.value,
      product_id: movTarget.value.products.id,
      type: movForm.value.type,
      quantity: Number(movForm.value.quantity),
      reason: movForm.value.reason || null,
    })
    showMovementModal.value = false
    await load()
  } finally { saving.value = false }
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('el-GR', { day: '2-digit', month: 'short' })
}

const movTypes = ['inbound', 'outbound', 'adjustment'] as const
</script>

<template>
  <div class="page">

    <div class="page-header">
      <div class="header-icon">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <rect x="2" y="7" width="20" height="14" rx="2"/>
          <path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/>
          <line x1="12" y1="12" x2="12" y2="16"/>
          <line x1="10" y1="14" x2="14" y2="14"/>
        </svg>
      </div>
      <div>
        <h1 class="page-title">{{ t('nav.inventory') }}</h1>
        <p class="page-sub">{{ t('wms.inventory.subtitle') }}</p>
      </div>
    </div>

    <!-- AI Suggestions panel -->
    <div v-if="suggestions.length > 0" class="ai-panel">
      <div class="ai-panel-head">
        <div class="ai-panel-icon">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        </div>
        <div>
          <p class="ai-panel-title">{{ t('wms.inventory.ai.title') }}</p>
          <p class="ai-panel-sub">{{ t('wms.inventory.ai.subtitle') }}</p>
        </div>
      </div>
      <div class="ai-items">
        <div v-for="s in suggestions" :key="s.product_id" class="ai-item">
          <span class="urgency-badge" :class="`urgency--${s.urgency}`">
            {{ t(`wms.inventory.ai.${s.urgency}`) }}
          </span>
          <div class="ai-item-info">
            <span class="ai-item-sku">{{ s.sku }}</span>
            <span class="ai-item-name">{{ s.name }}</span>
          </div>
          <div class="ai-item-stats">
            <span class="stat-pill">
              {{ t('wms.inventory.ai.currentStock') }}: <strong>{{ s.current_stock }} {{ s.unit }}</strong>
            </span>
            <span class="stat-pill">
              {{ t('wms.inventory.ai.reorderPoint') }}: <strong>{{ s.reorder_point }}</strong>
            </span>
            <span v-if="s.days_until_stockout != null" class="stat-pill stat-pill--warn">
              {{ t('wms.inventory.ai.daysLeft', { days: s.days_until_stockout }) }}
            </span>
            <span v-else class="stat-pill stat-pill--muted">
              {{ t('wms.inventory.ai.noHistory') }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="state-msg">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="state-msg state-msg--error">{{ error }}</div>

    <div v-else-if="items.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="2" y="7" width="20" height="14" rx="2"/>
          <path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/>
        </svg>
      </div>
      <p class="empty-title">{{ t('wms.inventory.empty.title') }}</p>
      <p class="empty-hint">{{ t('wms.inventory.empty.hint') }}</p>
    </div>

    <div v-else class="card">
      <div class="tbl-wrap">
        <table class="tbl">
          <thead>
            <tr>
              <th>{{ t('wms.inventory.table.sku') }}</th>
              <th>{{ t('wms.inventory.table.name') }}</th>
              <th>{{ t('wms.inventory.table.category') }}</th>
              <th class="num">{{ t('wms.inventory.table.quantity') }}</th>
              <th class="num">{{ t('wms.inventory.table.reorderPoint') }}</th>
              <th>{{ t('wms.inventory.table.lastUpdated') }}</th>
              <th class="act"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td><span class="sku-badge">{{ item.products.sku }}</span></td>
              <td class="fw">{{ item.products.name }}</td>
              <td class="muted">{{ item.products.category || '—' }}</td>
              <td class="num">
                <span class="qty-val"
                  :class="{ 'qty--low': item.quantity <= item.products.reorder_point }">
                  {{ item.quantity }}
                </span>
                <span class="muted"> {{ item.products.unit }}</span>
              </td>
              <td class="num muted">{{ item.products.reorder_point }}</td>
              <td class="muted">{{ fmtDate(item.last_updated) }}</td>
              <td class="act">
                <div class="row-actions">
                  <button class="btn-sm" @click="openMovement(item)">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    Mov
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Movement Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showMovementModal" class="modal-overlay" @click.self="showMovementModal = false">
          <div class="modal">
            <div class="modal-head">
              <div>
                <h2 class="modal-title">{{ t('wms.inventory.movement.title') }}</h2>
                <p v-if="movTarget" class="modal-sub">{{ movTarget.products.name }}</p>
              </div>
              <button class="icon-btn" @click="showMovementModal = false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <div class="modal-body">
              <div class="form-row">
                <label class="label">{{ t('wms.inventory.movement.type') }}</label>
                <div class="type-pills">
                  <button v-for="mt in movTypes" :key="mt"
                    :class="['type-pill', { active: movForm.type === mt }]"
                    @click="movForm.type = mt">
                    {{ t(`wms.inventory.movement.${mt}`) }}
                  </button>
                </div>
              </div>
              <div class="form-row">
                <label class="label">{{ t('wms.inventory.movement.quantity') }}</label>
                <input v-model="movForm.quantity" class="input" type="number" min="1" />
              </div>
              <div class="form-row">
                <label class="label">{{ t('wms.inventory.movement.reason') }}</label>
                <input v-model="movForm.reason" class="input" :placeholder="t('wms.inventory.movement.reasonPlaceholder')" />
              </div>
            </div>
            <div class="modal-foot">
              <button class="btn-ghost" @click="showMovementModal = false">{{ t('common.cancel') }}</button>
              <button class="btn-primary" :disabled="saving" @click="saveMovement">
                {{ saving ? t('common.loading') : t('common.save') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

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

/* AI Panel */
.ai-panel {
  background: rgba(62,207,191,.04);
  border: 1px solid rgba(62,207,191,.18);
  border-radius: var(--r-lg);
  padding: 1rem 1.25rem;
  display: flex; flex-direction: column; gap: .9rem;
}
.ai-panel-head { display: flex; align-items: flex-start; gap: .75rem; }
.ai-panel-icon {
  width: 28px; height: 28px;
  background: rgba(62,207,191,.12); border-radius: var(--r);
  display: flex; align-items: center; justify-content: center;
  color: var(--teal); flex-shrink: 0; margin-top: .05rem;
}
.ai-panel-title { font-size: .82rem; font-weight: 600; color: var(--teal); margin: 0; }
.ai-panel-sub   { font-size: .72rem; color: var(--text-muted); margin: .15rem 0 0; }

.ai-items { display: flex; flex-direction: column; gap: .55rem; }
.ai-item {
  display: flex; align-items: center; gap: .8rem; flex-wrap: wrap;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--r); padding: .6rem .85rem;
}
.urgency-badge {
  font-size: .65rem; font-weight: 700; padding: .15rem .5rem;
  border-radius: 999px; letter-spacing: .04em; text-transform: uppercase;
  flex-shrink: 0;
}
.urgency--critical { background: var(--red-bg); color: var(--red); border: 1px solid rgba(224,85,85,.25); }
.urgency--warning  { background: rgba(212,160,23,.1); color: var(--amber); border: 1px solid rgba(212,160,23,.25); }

.ai-item-info { display: flex; align-items: center; gap: .5rem; flex: 1; min-width: 0; }
.ai-item-sku  { font-size: .7rem; color: var(--teal); font-family: monospace; font-weight: 600; }
.ai-item-name { font-size: .8rem; color: var(--text); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.ai-item-stats { display: flex; align-items: center; gap: .4rem; flex-wrap: wrap; }
.stat-pill {
  font-size: .7rem; color: var(--text-muted);
  background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--r); padding: .1rem .45rem;
}
.stat-pill strong { color: var(--text-sub); }
.stat-pill--warn  { color: var(--red); border-color: rgba(224,85,85,.2); background: var(--red-bg); }
.stat-pill--muted { color: var(--text-muted); }

/* State */
.state-msg { font-size: .82rem; color: var(--text-muted); padding: 2rem; text-align: center; }
.state-msg--error { color: var(--red); }

.empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: .75rem; padding: 3rem 1rem;
}
.empty-icon {
  width: 48px; height: 48px; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--r-xl); display: flex; align-items: center; justify-content: center;
  color: var(--text-muted);
}
.empty-title { font-size: .92rem; font-weight: 600; color: var(--text); margin: 0; }
.empty-hint  { font-size: .78rem; color: var(--text-muted); margin: 0; }

/* Table */
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--r-lg); overflow: hidden; }
.tbl-wrap { overflow-x: auto; }
.tbl { width: 100%; border-collapse: collapse; font-size: .8rem; }
.tbl thead { background: var(--bg); border-bottom: 1px solid var(--border); }
.tbl th {
  padding: .65rem 1rem; font-size: .66rem; font-weight: 600;
  color: var(--text-muted); letter-spacing: .06em; text-transform: uppercase;
  text-align: left; white-space: nowrap;
}
.tbl th.num, .tbl td.num { text-align: right; }
.tbl th.act, .tbl td.act { width: 80px; text-align: right; padding-right: .75rem; }
.tbl td { padding: .72rem 1rem; color: var(--text-sub); border-bottom: 1px solid var(--border); }
.tbl tbody tr:last-child td { border-bottom: none; }
.tbl tbody tr:hover { background: var(--bg-hover); }
.tbl td.fw    { color: var(--text); font-weight: 500; }
.tbl td.muted { color: var(--text-muted); }

.sku-badge {
  display: inline-block; background: rgba(62,207,191,.08); border: 1px solid rgba(62,207,191,.2);
  color: var(--teal); font-size: .71rem; font-weight: 600; padding: .1rem .45rem;
  border-radius: var(--r); font-family: monospace; letter-spacing: .03em;
}

.qty-val { font-weight: 600; color: var(--text); }
.qty--low { color: var(--red); }

.row-actions { display: flex; align-items: center; justify-content: flex-end; opacity: 0; transition: opacity .15s; }
.tbl tbody tr:hover .row-actions { opacity: 1; }

.btn-sm {
  display: inline-flex; align-items: center; gap: .25rem;
  background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--r); color: var(--text-sub);
  font-size: .72rem; font-weight: 500; padding: .28rem .6rem;
  cursor: pointer; transition: border-color .15s, color .15s;
}
.btn-sm:hover { border-color: var(--teal); color: var(--teal); }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.6);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 1rem;
}
.modal {
  background: var(--bg-card); border: 1px solid var(--border-mid);
  border-radius: var(--r-xl); width: 100%; max-width: 400px;
  box-shadow: var(--shadow-lg);
}
.modal-head {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 1rem 1.25rem; border-bottom: 1px solid var(--border);
}
.modal-title { font-size: .92rem; font-weight: 600; color: var(--text); margin: 0; }
.modal-sub   { font-size: .72rem; color: var(--text-muted); margin: .15rem 0 0; }
.modal-body  { padding: 1.25rem; display: flex; flex-direction: column; gap: .8rem; }
.modal-foot  { display: flex; justify-content: flex-end; gap: .5rem; padding: .8rem 1.25rem; border-top: 1px solid var(--border); }

.form-row { display: flex; flex-direction: column; gap: .28rem; }
.label { font-size: .71rem; font-weight: 500; color: var(--text-sub); }

.type-pills { display: flex; gap: .4rem; }
.type-pill {
  flex: 1; background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--r); color: var(--text-muted); font-size: .76rem;
  padding: .45rem .5rem; cursor: pointer; transition: all .15s; text-align: center;
}
.type-pill.active {
  background: rgba(62,207,191,.1); border-color: rgba(62,207,191,.35);
  color: var(--teal); font-weight: 600;
}
.type-pill:hover:not(.active) { border-color: var(--border-mid); color: var(--text-sub); }

.input {
  background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--r); color: var(--text); font-size: .82rem;
  padding: .48rem .7rem; outline: none; transition: border-color .15s;
  width: 100%; box-sizing: border-box;
}
.input:focus { border-color: var(--teal); }
.input::placeholder { color: var(--text-muted); }

.btn-primary {
  display: inline-flex; align-items: center; gap: .4rem;
  background: var(--teal); color: #0a0a0a; border: none;
  border-radius: var(--r); padding: .5rem 1rem;
  font-size: .8rem; font-weight: 600; cursor: pointer; transition: opacity .15s;
}
.btn-primary:hover { opacity: .88; }
.btn-primary:disabled { opacity: .45; cursor: not-allowed; }

.btn-ghost {
  background: transparent; border: 1px solid var(--border);
  color: var(--text-sub); border-radius: var(--r);
  padding: .5rem 1rem; font-size: .8rem; cursor: pointer;
  transition: border-color .15s;
}
.btn-ghost:hover { border-color: var(--border-mid); }

.icon-btn {
  width: 26px; height: 26px; background: transparent; border: 1px solid transparent;
  border-radius: var(--r); display: flex; align-items: center; justify-content: center;
  color: var(--text-muted); cursor: pointer; transition: background .12s, color .12s;
}
.icon-btn:hover { background: var(--bg-hover); border-color: var(--border); color: var(--text-sub); }

.modal-enter-active { transition: all .18s cubic-bezier(.2,.8,.3,1); }
.modal-leave-active { transition: all .12s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal { transform: scale(.94) translateY(8px); }
</style>
