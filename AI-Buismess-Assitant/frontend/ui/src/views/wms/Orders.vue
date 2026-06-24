<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { api } from '@/services/api'

const auth = useAuthStore()
const { t } = useI18n()

interface Order {
  id: string; type: 'purchase' | 'sale'; status: string
  party_name: string | null; notes: string | null; created_at: string
}

interface Product { id: string; sku: string; name: string; unit: string }

interface LineItem { product_id: string; quantity: number; unit_price: string }

const orders    = ref<Order[]>([])
const products  = ref<Product[]>([])
const loading   = ref(true)
const error     = ref('')
const tab       = ref<'all' | 'purchase' | 'sale'>('all')
const showModal = ref(false)
const saving    = ref(false)
const completing = ref<string | null>(null)

const form = ref({
  type: 'purchase' as 'purchase' | 'sale',
  party_name: '',
  notes: '',
  items: [{ product_id: '', quantity: 1, unit_price: '' }] as LineItem[],
})

const businessId = computed(() => auth.currentBusiness?.id ?? '')

const filtered = computed(() => {
  if (tab.value === 'all') return orders.value
  return orders.value.filter(o => o.type === tab.value)
})

async function load() {
  if (!businessId.value) { loading.value = false; return }
  loading.value = true; error.value = ''
  try {
    const [ordRes, prdRes] = await Promise.allSettled([
      api.get('/orders', { params: { business_id: businessId.value } }),
      api.get('/products', { params: { business_id: businessId.value } }),
    ])
    orders.value   = ordRes.status === 'fulfilled' ? ordRes.value.data : []
    products.value = prdRes.status === 'fulfilled' ? prdRes.value.data : []
  } catch { error.value = t('wms.errorLoad') }
  finally { loading.value = false }
}

onMounted(load)

function openCreate() {
  form.value = {
    type: 'purchase', party_name: '', notes: '',
    items: [{ product_id: '', quantity: 1, unit_price: '' }],
  }
  showModal.value = true
}

function addItem() {
  form.value.items.push({ product_id: '', quantity: 1, unit_price: '' })
}

function removeItem(i: number) {
  if (form.value.items.length > 1) form.value.items.splice(i, 1)
}

async function save() {
  saving.value = true
  try {
    const validItems = form.value.items
      .filter(it => it.product_id)
      .map(it => ({
        product_id: it.product_id,
        quantity: Number(it.quantity),
        unit_price: it.unit_price !== '' ? Number(it.unit_price) : null,
      }))
    await api.post('/orders', {
      business_id: businessId.value,
      type: form.value.type,
      party_name: form.value.party_name || null,
      notes: form.value.notes || null,
      items: validItems,
    })
    showModal.value = false
    await load()
  } finally { saving.value = false }
}

async function completeOrder(id: string) {
  completing.value = id
  try {
    await api.post(`/orders/${id}/complete`, {})
    await load()
  } finally { completing.value = null }
}

async function cancelOrder(id: string) {
  try {
    await api.patch(`/orders/${id}/status`, { status: 'cancelled' })
    await load()
  } catch { /* ignore */ }
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('el-GR', { day: '2-digit', month: 'short', year: '2-digit' })
}

const STATUS_CLASS: Record<string, string> = {
  draft: 'status--draft',
  confirmed: 'status--confirmed',
  completed: 'status--completed',
  cancelled: 'status--cancelled',
}
</script>

<template>
  <div class="page">

    <div class="page-header">
      <div class="header-icon">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="9" y1="13" x2="15" y2="13"/>
          <line x1="9" y1="17" x2="15" y2="17"/>
        </svg>
      </div>
      <div class="header-text">
        <h1 class="page-title">{{ t('nav.orders') }}</h1>
        <p class="page-sub">{{ t('wms.orders.subtitle') }}</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        {{ t('wms.orders.addBtn') }}
      </button>
    </div>

    <!-- Tabs -->
    <div class="tabs-row">
      <div class="tabs">
        <button v-for="tb in ['all', 'purchase', 'sale'] as const" :key="tb"
          :class="['tab', { active: tab === tb }]" @click="tab = tb">
          {{ t(`wms.orders.tabs.${tb}`) }}
          <span v-if="tb !== 'all'" class="tab-count">
            {{ orders.filter(o => o.type === tb).length }}
          </span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="state-msg">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="state-msg state-msg--error">{{ error }}</div>

    <div v-else-if="filtered.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
      </div>
      <p class="empty-title">{{ t('wms.orders.empty.title') }}</p>
      <p class="empty-hint">{{ t('wms.orders.empty.hint') }}</p>
      <button class="btn-primary" @click="openCreate">{{ t('wms.orders.addBtn') }}</button>
    </div>

    <div v-else class="card">
      <div class="tbl-wrap">
        <table class="tbl">
          <thead>
            <tr>
              <th>{{ t('wms.orders.table.id') }}</th>
              <th>{{ t('wms.orders.table.type') }}</th>
              <th>{{ t('wms.orders.table.party') }}</th>
              <th>{{ t('wms.orders.table.status') }}</th>
              <th>{{ t('wms.orders.table.date') }}</th>
              <th class="act"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="o in filtered" :key="o.id">
              <td><span class="order-id">#{{ o.id.slice(0, 8) }}</span></td>
              <td>
                <span class="type-badge" :class="o.type === 'purchase' ? 'type--purchase' : 'type--sale'">
                  {{ t(`wms.orders.type.${o.type}`) }}
                </span>
              </td>
              <td class="fw">{{ o.party_name || '—' }}</td>
              <td>
                <span class="status-badge" :class="STATUS_CLASS[o.status]">
                  {{ t(`wms.orders.status.${o.status}`) }}
                </span>
              </td>
              <td class="muted">{{ fmtDate(o.created_at) }}</td>
              <td class="act">
                <div class="row-actions">
                  <template v-if="o.status !== 'completed' && o.status !== 'cancelled'">
                    <button class="btn-sm btn-sm--confirm"
                      :disabled="completing === o.id"
                      @click="completeOrder(o.id)">
                      {{ completing === o.id ? '…' : t('common.complete') }}
                    </button>
                    <button class="btn-sm btn-sm--cancel" @click="cancelOrder(o.id)">
                      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                      </svg>
                    </button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- New Order Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
          <div class="modal">
            <div class="modal-head">
              <h2 class="modal-title">{{ t('wms.orders.modal.title') }}</h2>
              <button class="icon-btn" @click="showModal = false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <div class="modal-body">
              <div class="form-row">
                <label class="label">{{ t('wms.orders.modal.orderType') }}</label>
                <div class="type-pills">
                  <button :class="['type-pill', { active: form.type === 'purchase' }]" @click="form.type = 'purchase'">
                    {{ t('wms.orders.type.purchase') }}
                  </button>
                  <button :class="['type-pill', { active: form.type === 'sale' }]" @click="form.type = 'sale'">
                    {{ t('wms.orders.type.sale') }}
                  </button>
                </div>
              </div>
              <div class="form-row">
                <label class="label">{{ t('wms.orders.modal.party') }}</label>
                <input v-model="form.party_name" class="input" :placeholder="t('wms.orders.modal.partyPlaceholder')" />
              </div>

              <div class="items-section">
                <div class="items-head">
                  <span class="label">{{ t('wms.orders.modal.items') }}</span>
                  <button class="btn-link" @click="addItem">+ {{ t('wms.orders.modal.addItem') }}</button>
                </div>
                <div v-if="products.length === 0" class="muted-note">{{ t('wms.orders.modal.noProducts') }}</div>
                <div v-for="(item, i) in form.items" :key="i" class="item-row">
                  <select v-model="item.product_id" class="input select flex-grow">
                    <option value="">{{ t('wms.orders.modal.product') }}…</option>
                    <option v-for="p in products" :key="p.id" :value="p.id">{{ p.sku }} — {{ p.name }}</option>
                  </select>
                  <input v-model="item.quantity" class="input qty-input" type="number" min="1"
                    :placeholder="t('wms.orders.modal.quantity')" />
                  <input v-model="item.unit_price" class="input price-input" type="number" step="0.01" min="0"
                    placeholder="€" />
                  <button v-if="form.items.length > 1" class="icon-btn icon-btn--danger" @click="removeItem(i)">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                  </button>
                </div>
              </div>

              <div class="form-row">
                <label class="label">{{ t('wms.orders.modal.notes') }}</label>
                <input v-model="form.notes" class="input" :placeholder="t('wms.orders.modal.notesPlaceholder')" />
              </div>
            </div>
            <div class="modal-foot">
              <button class="btn-ghost" @click="showModal = false">{{ t('common.cancel') }}</button>
              <button class="btn-primary" :disabled="saving" @click="save">
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
.header-text { flex: 1; }
.page-title { font-size: 1.2rem; font-weight: 600; color: var(--text); margin: 0; letter-spacing: -.01em; }
.page-sub   { font-size: .75rem; color: var(--text-muted); margin: .15rem 0 0; }

/* Tabs */
.tabs-row { display: flex; }
.tabs {
  display: inline-flex; gap: .2rem;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: .25rem;
}
.tab {
  display: inline-flex; align-items: center; gap: .4rem;
  background: transparent; border: none; border-radius: var(--r);
  color: var(--text-muted); font-size: .78rem; font-weight: 500;
  padding: .35rem .8rem; cursor: pointer; transition: all .15s;
}
.tab:hover { color: var(--text-sub); }
.tab.active { background: var(--bg-hover); color: var(--text); font-weight: 600; }
.tab-count {
  font-size: .66rem; background: var(--bg); border: 1px solid var(--border);
  border-radius: 999px; padding: .05rem .35rem; color: var(--text-muted);
}

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
.tbl th.act, .tbl td.act { width: 120px; text-align: right; padding-right: .75rem; }
.tbl td { padding: .72rem 1rem; color: var(--text-sub); border-bottom: 1px solid var(--border); }
.tbl tbody tr:last-child td { border-bottom: none; }
.tbl tbody tr:hover { background: var(--bg-hover); }
.tbl td.fw    { color: var(--text); font-weight: 500; }
.tbl td.muted { color: var(--text-muted); }

.order-id { font-family: monospace; font-size: .78rem; color: var(--text-muted); }

.type-badge {
  display: inline-block; font-size: .68rem; font-weight: 600;
  padding: .1rem .45rem; border-radius: var(--r); text-transform: uppercase; letter-spacing: .03em;
}
.type--purchase { background: rgba(62,207,191,.1); color: var(--teal); border: 1px solid rgba(62,207,191,.2); }
.type--sale     { background: rgba(58,184,122,.1); color: var(--green); border: 1px solid rgba(58,184,122,.2); }

.status-badge {
  display: inline-block; font-size: .68rem; font-weight: 600;
  padding: .1rem .45rem; border-radius: var(--r); letter-spacing: .02em;
}
.status--draft     { background: var(--bg); color: var(--text-muted); border: 1px solid var(--border); }
.status--confirmed { background: rgba(62,207,191,.1); color: var(--teal); border: 1px solid rgba(62,207,191,.2); }
.status--completed { background: var(--green-bg); color: var(--green); border: 1px solid rgba(58,184,122,.2); }
.status--cancelled { background: var(--red-bg); color: var(--red); border: 1px solid rgba(224,85,85,.2); }

.row-actions { display: flex; align-items: center; justify-content: flex-end; gap: .3rem; opacity: 0; transition: opacity .15s; }
.tbl tbody tr:hover .row-actions { opacity: 1; }

.btn-sm {
  display: inline-flex; align-items: center; gap: .25rem;
  background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--r); color: var(--text-sub);
  font-size: .72rem; font-weight: 500; padding: .28rem .6rem;
  cursor: pointer; transition: border-color .15s, color .15s;
}
.btn-sm:disabled { opacity: .5; cursor: not-allowed; }
.btn-sm--confirm:hover { border-color: var(--green); color: var(--green); }
.btn-sm--cancel:hover  { border-color: var(--red); color: var(--red); }

/* Buttons */
.btn-primary {
  display: inline-flex; align-items: center; gap: .4rem;
  background: var(--teal); color: #0a0a0a; border: none;
  border-radius: var(--r); padding: .5rem 1rem;
  font-size: .8rem; font-weight: 600; cursor: pointer; transition: opacity .15s; white-space: nowrap;
}
.btn-primary:hover { opacity: .88; }
.btn-primary:disabled { opacity: .45; cursor: not-allowed; }

.btn-ghost {
  background: transparent; border: 1px solid var(--border);
  color: var(--text-sub); border-radius: var(--r); padding: .5rem 1rem;
  font-size: .8rem; cursor: pointer; transition: border-color .15s;
}
.btn-ghost:hover { border-color: var(--border-mid); }

.btn-link {
  background: transparent; border: none; color: var(--teal);
  font-size: .75rem; cursor: pointer; padding: 0;
}
.btn-link:hover { opacity: .75; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.6);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 1rem;
}
.modal {
  background: var(--bg-card); border: 1px solid var(--border-mid);
  border-radius: var(--r-xl); width: 100%; max-width: 520px;
  max-height: 90vh; overflow-y: auto;
  box-shadow: var(--shadow-lg);
}
.modal-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.25rem; border-bottom: 1px solid var(--border);
  position: sticky; top: 0; background: var(--bg-card); z-index: 1;
}
.modal-title { font-size: .92rem; font-weight: 600; color: var(--text); margin: 0; }
.modal-body  { padding: 1.25rem; display: flex; flex-direction: column; gap: .8rem; }
.modal-foot  { display: flex; justify-content: flex-end; gap: .5rem; padding: .8rem 1.25rem; border-top: 1px solid var(--border); position: sticky; bottom: 0; background: var(--bg-card); }

.form-row { display: flex; flex-direction: column; gap: .28rem; }
.label { font-size: .71rem; font-weight: 500; color: var(--text-sub); }

.type-pills { display: flex; gap: .4rem; }
.type-pill {
  flex: 1; background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--r); color: var(--text-muted); font-size: .76rem;
  padding: .45rem .5rem; cursor: pointer; transition: all .15s; text-align: center;
}
.type-pill.active { background: rgba(62,207,191,.1); border-color: rgba(62,207,191,.35); color: var(--teal); font-weight: 600; }
.type-pill:hover:not(.active) { border-color: var(--border-mid); color: var(--text-sub); }

/* Line items */
.items-section { display: flex; flex-direction: column; gap: .5rem; }
.items-head    { display: flex; align-items: center; justify-content: space-between; }
.muted-note    { font-size: .76rem; color: var(--text-muted); font-style: italic; }
.item-row      { display: flex; gap: .4rem; align-items: center; }
.flex-grow     { flex: 1; }
.qty-input     { width: 70px; flex-shrink: 0; }
.price-input   { width: 80px; flex-shrink: 0; }

.input {
  background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--r); color: var(--text); font-size: .82rem;
  padding: .48rem .7rem; outline: none; transition: border-color .15s;
  box-sizing: border-box;
}
.input:focus { border-color: var(--teal); }
.input::placeholder { color: var(--text-muted); }
.select { cursor: pointer; }
.select option { background: var(--bg-card); }

.icon-btn {
  width: 26px; height: 26px; background: transparent; border: 1px solid transparent;
  border-radius: var(--r); display: flex; align-items: center; justify-content: center;
  color: var(--text-muted); cursor: pointer; transition: background .12s, color .12s; flex-shrink: 0;
}
.icon-btn:hover { background: var(--bg-hover); border-color: var(--border); color: var(--text-sub); }
.icon-btn--danger:hover { background: var(--red-bg); border-color: rgba(224,85,85,.25); color: var(--red); }

.modal-enter-active { transition: all .18s cubic-bezier(.2,.8,.3,1); }
.modal-leave-active { transition: all .12s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal { transform: scale(.94) translateY(8px); }
</style>
