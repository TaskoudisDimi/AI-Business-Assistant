<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseModal from '@/components/ui/BaseModal.vue'
import { api } from '@/services/api'
import { apiErrorMessage } from '@/stores/auth'

interface Product { id: string; sku: string; name: string; unit: string }
interface Line {
  description: string; code: string | null; quantity: number; unit: string | null; unit_price: number | null
  match: { product_id: string; by: 'sku' | 'barcode' | 'name'; score: number } | null
}
interface Row { include: boolean; product_id: string; quantity: number; unit_price: string; line: Line }

const props = defineProps<{ businessId: string; products: Product[] }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'created'): void }>()
const { t, locale } = useI18n()

const file = ref<File | null>(null)
const preview = ref('')
const reading = ref(false)
const saving = ref(false)
const error = ref('')
const doc = ref<{ supplier_name: string | null; document_number: string | null; document_date: string | null; warnings: string[] } | null>(null)
const rows = ref<Row[]>([])
const supplier = ref('')

function onPick(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  file.value = f
  preview.value = f.type.startsWith('image/') ? URL.createObjectURL(f) : ''
  read()
}

async function read() {
  if (!file.value) return
  reading.value = true; error.value = ''; doc.value = null; rows.value = []
  const fd = new FormData()
  fd.append('business_id', props.businessId)
  fd.append('language', locale.value)
  fd.append('file', file.value)
  try {
    const { data } = await api.post('/ai/scan-invoice', fd, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 180_000 })
    doc.value = data
    supplier.value = data.supplier_name ?? ''
    rows.value = (data.lines as Line[]).map(l => ({
      include: !!l.match, product_id: l.match?.product_id ?? '',
      quantity: Math.max(1, Math.round(l.quantity)), unit_price: l.unit_price != null ? String(l.unit_price) : '', line: l,
    }))
  } catch (e) {
    error.value = apiErrorMessage(e) || t('common.error')
  } finally { reading.value = false }
}

const ready = computed(() => rows.value.filter(r => r.include && r.product_id && r.quantity > 0))

async function createOrder() {
  saving.value = true; error.value = ''
  try {
    await api.post('/orders', {
      business_id: props.businessId, type: 'purchase',
      party_name: supplier.value || null,
      notes: doc.value?.document_number ? t('scanInvoice.noteRef', { n: doc.value.document_number }) : null,
      items: ready.value.map(r => ({ product_id: r.product_id, quantity: r.quantity,
        unit_price: r.unit_price !== '' ? Number(r.unit_price) : null })),
    })
    emit('created')
    emit('close')
  } catch (e) {
    error.value = apiErrorMessage(e) || t('common.error')
  } finally { saving.value = false }
}
</script>

<template>
  <BaseModal :title="t('scanInvoice.title')" :subtitle="t('scanInvoice.subtitle')" :width="860" @close="emit('close')">
    <div class="pick">
      <label class="ui-btn" :class="file ? 'ui-btn--ghost' : 'ui-btn--primary'">
        <input type="file" accept="image/*,application/pdf" hidden @change="onPick" />
        {{ file ? t('scanInvoice.another') : t('scanInvoice.choose') }}
      </label>
      <span v-if="file" class="ui-muted">{{ file.name }}</span>
    </div>

    <div v-if="reading" class="reading">
      <span class="ui-spinner" /> {{ t('scanInvoice.reading') }}
    </div>
    <p v-if="error" class="ui-alert ui-alert--error">{{ error }}</p>

    <template v-if="doc">
      <div class="meta">
        <img v-if="preview" :src="preview" alt="" class="thumb" />
        <div class="meta-fields">
          <div class="ui-field">
            <label class="ui-label">{{ t('scanInvoice.supplier') }}</label>
            <input v-model="supplier" class="ui-input ui-input--sm" />
          </div>
          <p class="ui-muted small">
            <span v-if="doc.document_number">{{ t('scanInvoice.number') }}: {{ doc.document_number }}</span>
            <span v-if="doc.document_date"> · {{ doc.document_date }}</span>
          </p>
        </div>
      </div>
      <p v-for="w in doc.warnings" :key="w" class="ui-alert ui-alert--warn">{{ w }}</p>

      <div class="ui-card">
        <div class="ui-table-wrap">
          <table class="ui-table">
            <thead><tr>
              <th></th><th>{{ t('scanInvoice.onDocument') }}</th><th>{{ t('scanInvoice.product') }}</th>
              <th class="num">{{ t('wms.inventory.table.quantity') }}</th><th class="num">{{ t('scanInvoice.price') }}</th>
            </tr></thead>
            <tbody>
              <tr v-for="(r, i) in rows" :key="i" :class="{ off: !r.include }">
                <td><input v-model="r.include" type="checkbox" :aria-label="t('scanInvoice.include')" /></td>
                <td>
                  <div>{{ r.line.description }}</div>
                  <div class="ui-muted small">
                    <span v-if="r.line.code" class="ui-mono">{{ r.line.code }}</span>
                    {{ r.line.quantity }} {{ r.line.unit ?? '' }}
                  </div>
                </td>
                <td>
                  <select v-model="r.product_id" class="ui-select ui-input--sm" @change="r.include = !!r.product_id">
                    <option value="">{{ t('scanInvoice.noMatch') }}</option>
                    <option v-for="p in products" :key="p.id" :value="p.id">{{ p.sku }} · {{ p.name }}</option>
                  </select>
                  <span v-if="r.line.match?.by === 'name'" class="ui-badge ui-badge--amber guess">{{ t('scanInvoice.guess') }}</span>
                </td>
                <td class="num"><input v-model.number="r.quantity" class="ui-input ui-input--sm qty" type="number" min="1" /></td>
                <td class="num"><input v-model="r.unit_price" class="ui-input ui-input--sm qty" type="number" step="0.01" min="0" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <p class="ui-hint">{{ t('scanInvoice.review') }}</p>
    </template>

    <template #footer>
      <button class="ui-btn ui-btn--ghost" @click="emit('close')">{{ t('common.cancel') }}</button>
      <button class="ui-btn ui-btn--primary" :disabled="!ready.length || saving" @click="createOrder">
        <span v-if="saving" class="ui-spinner" />{{ t('scanInvoice.create', { n: ready.length }) }}
      </button>
    </template>
  </BaseModal>
</template>

<style scoped>
.pick { display: flex; align-items: center; gap: .75rem; }
.pick label { cursor: pointer; }
.reading { display: flex; align-items: center; gap: .6rem; color: var(--text-sub); font-size: .9rem; }
.meta { display: flex; gap: 1rem; align-items: flex-start; }
.thumb { width: 96px; height: 120px; object-fit: cover; border-radius: var(--r); border: 1px solid var(--border); }
.meta-fields { flex: 1; display: flex; flex-direction: column; gap: .5rem; max-width: 360px; }
.small { font-size: .8rem; }
.qty { width: 90px; text-align: right; margin-left: auto; }
.guess { margin-top: .25rem; }
tr.off td { opacity: .5; }
</style>
