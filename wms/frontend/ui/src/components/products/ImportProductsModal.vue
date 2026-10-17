<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Papa from 'papaparse'
import BaseModal from '@/components/ui/BaseModal.vue'
import { api } from '@/services/api'
import { apiErrorMessage } from '@/stores/auth'

const props = defineProps<{ businessId: string }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'imported'): void }>()
const { t } = useI18n()

type Field = 'sku' | 'name' | 'category' | 'unit' | 'reorder_point' | 'cost_price' | 'sell_price'
  | 'barcode' | 'supplier' | 'lead_time_days' | 'initial_stock'
const FIELDS: Field[] = ['sku', 'name', 'category', 'unit', 'barcode', 'supplier', 'cost_price', 'sell_price',
  'reorder_point', 'lead_time_days', 'initial_stock']
const NUMERIC: Field[] = ['reorder_point', 'cost_price', 'sell_price', 'lead_time_days', 'initial_stock']

// Header names we recognise automatically (lower-case, accents stripped)
const ALIASES: Record<Field, string[]> = {
  sku: ['sku', 'κωδικος', 'κωδ', 'code', 'item code', 'κωδικος ειδους'],
  name: ['name', 'ονομα', 'περιγραφη', 'description', 'προιον', 'product', 'ειδος'],
  category: ['category', 'κατηγορια', 'ομαδα'],
  unit: ['unit', 'μοναδα', 'μμ', 'μ.μ.'],
  barcode: ['barcode', 'ean', 'ean13', 'upc', 'γραμμωτος', 'γραμμωτος κωδικος'],
  supplier: ['supplier', 'προμηθευτης', 'vendor'],
  cost_price: ['cost', 'cost price', 'κοστος', 'τιμη αγορας', 'τιμη κοστους'],
  sell_price: ['price', 'sell price', 'τιμη', 'τιμη πωλησης', 'λιανικη'],
  reorder_point: ['reorder point', 'reorder', 'οριο', 'οριο αναπαραγγελιας', 'ελαχιστο', 'min'],
  lead_time_days: ['lead time', 'lead time days', 'χρονος παραδοσης', 'ημερες παραδοσης'],
  initial_stock: ['stock', 'quantity', 'qty', 'αποθεμα', 'ποσοτητα', 'υπολοιπο'],
}

const norm = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[_:]/g, ' ').trim()

const fileName = ref('')
const headers = ref<string[]>([])
const rows = ref<unknown[][]>([])
const mapping = ref<Record<Field, number | null>>(Object.fromEntries(FIELDS.map(f => [f, null])) as Record<Field, number | null>)
const updateExisting = ref(true)
const parsing = ref(false)
const saving = ref(false)
const error = ref('')
const result = ref<{ created: number; updated: number; skipped: number } | null>(null)

function autoMap() {
  const used = new Set<number>()
  for (const f of FIELDS) {
    const idx = headers.value.findIndex((h, i) => !used.has(i) && ALIASES[f].includes(norm(h)))
    mapping.value[f] = idx >= 0 ? idx : null
    if (idx >= 0) used.add(idx)
  }
}

async function onFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  error.value = ''; result.value = null; parsing.value = true; fileName.value = file.name
  try {
    let table: unknown[][]
    if (/\.xlsx$/i.test(file.name)) {
      const { readSheet } = await import('read-excel-file/browser')
      table = await readSheet(file)
    } else {
      const text = await file.text()
      table = Papa.parse<string[]>(text, { skipEmptyLines: 'greedy' }).data
    }
    if (table.length < 2) throw new Error(t('import.errors.empty'))
    headers.value = (table[0] ?? []).map(h => String(h ?? '').trim())
    rows.value = table.slice(1)
    autoMap()
  } catch (err) {
    error.value = err instanceof Error && err.message ? err.message : t('import.errors.read')
    headers.value = []; rows.value = []
  } finally {
    parsing.value = false
  }
}

/** "1.234,56" → 1234.56, "1234.56" → 1234.56, "12" → 12 */
function toNumber(v: unknown): number | null {
  if (v === null || v === undefined || v === '') return null
  if (typeof v === 'number') return v
  let s = String(v).trim().replace(/[€\s]/g, '')
  if (s.includes(',') && s.includes('.')) s = s.replace(/\./g, '').replace(',', '.')
  else if (s.includes(',')) s = s.replace(',', '.')
  const n = Number(s)
  return Number.isFinite(n) ? n : null
}

const parsed = computed(() => {
  const ok: Record<string, unknown>[] = []
  let invalid = 0
  for (const r of rows.value) {
    const cell = (f: Field) => { const i = mapping.value[f]; return i === null ? null : r[i] }
    const sku = String(cell('sku') ?? '').trim()
    const name = String(cell('name') ?? '').trim()
    if (!sku || !name) { invalid++; continue }
    const row: Record<string, unknown> = { sku, name }
    for (const f of FIELDS) {
      if (f === 'sku' || f === 'name' || mapping.value[f] === null) continue
      const v = cell(f)
      if (NUMERIC.includes(f)) {
        const n = toNumber(v)
        if (n !== null) row[f] = ['reorder_point', 'lead_time_days', 'initial_stock'].includes(f) ? Math.max(0, Math.round(n)) : Math.max(0, n)
      } else if (v !== null && String(v).trim()) {
        row[f] = String(v).trim()
      }
    }
    if (row.lead_time_days === 0) delete row.lead_time_days
    ok.push(row)
  }
  return { ok, invalid }
})

const canImport = computed(() => mapping.value.sku !== null && mapping.value.name !== null && parsed.value.ok.length > 0)

async function submit() {
  saving.value = true; error.value = ''
  try {
    const { data } = await api.post('/products/import', {
      business_id: props.businessId, rows: parsed.value.ok, update_existing: updateExisting.value,
    })
    result.value = data
    emit('imported')
  } catch (e) {
    error.value = apiErrorMessage(e) || t('common.error')
  } finally {
    saving.value = false
  }
}

function downloadTemplate() {
  const header = 'sku,name,category,unit,barcode,supplier,cost_price,sell_price,reorder_point,lead_time_days,initial_stock'
  const sample = 'CB-4030,Χαρτοκούτι 40x30x30,Συσκευασία,τεμ,5201234567890,Χαρτοποιία Αττικής,0.62,1.10,200,7,1200'
  const blob = new Blob(['﻿' + header + '\n' + sample + '\n'], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'products-template.csv'
  a.click()
  URL.revokeObjectURL(a.href)
}
</script>

<template>
  <BaseModal :title="t('import.title')" :subtitle="t('import.subtitle')" :width="760" @close="emit('close')">
    <template v-if="result">
      <p class="ui-alert ui-alert--success">
        {{ t('import.done', { created: result.created, updated: result.updated, skipped: result.skipped }) }}
      </p>
    </template>

    <template v-else>
      <div class="pick">
        <label class="ui-btn ui-btn--ghost">
          <input type="file" accept=".csv,.xlsx,text/csv" hidden @change="onFile" />
          {{ fileName ? t('import.change') : t('import.choose') }}
        </label>
        <span v-if="fileName" class="ui-muted">{{ fileName }} · {{ t('import.rows', { n: rows.length }) }}</span>
        <button class="link" type="button" @click="downloadTemplate">{{ t('import.template') }}</button>
      </div>
      <p v-if="parsing" class="ui-muted">{{ t('common.loading') }}</p>

      <template v-if="headers.length">
        <div>
          <p class="section-label">{{ t('import.mapping') }}</p>
          <div class="map-grid">
            <label v-for="f in FIELDS" :key="f" class="map-row">
              <span>{{ t(`import.fields.${f}`) }}<b v-if="f === 'sku' || f === 'name'"> *</b></span>
              <select v-model="mapping[f]" class="ui-select ui-input--sm">
                <option :value="null">—</option>
                <option v-for="(h, i) in headers" :key="i" :value="i">{{ h || `#${i + 1}` }}</option>
              </select>
            </label>
          </div>
        </div>

        <div v-if="parsed.ok.length" class="ui-card">
          <div class="ui-table-wrap">
            <table class="ui-table">
              <thead><tr><th>SKU</th><th>{{ t('import.fields.name') }}</th><th class="num">{{ t('import.fields.cost_price') }}</th><th class="num">{{ t('import.fields.sell_price') }}</th><th class="num">{{ t('import.fields.initial_stock') }}</th></tr></thead>
              <tbody>
                <tr v-for="(r, i) in parsed.ok.slice(0, 5)" :key="i">
                  <td class="ui-mono">{{ r.sku }}</td><td>{{ r.name }}</td>
                  <td class="num">{{ r.cost_price ?? '—' }}</td><td class="num">{{ r.sell_price ?? '—' }}</td>
                  <td class="num">{{ r.initial_stock ?? '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <p class="ui-muted small">
          {{ t('import.summary', { ok: parsed.ok.length }) }}
          <span v-if="parsed.invalid"> · {{ t('import.invalid', { n: parsed.invalid }) }}</span>
        </p>
        <label class="ui-check"><input v-model="updateExisting" type="checkbox" /> {{ t('import.updateExisting') }}</label>
      </template>
    </template>

    <p v-if="error" class="ui-alert ui-alert--error">{{ error }}</p>

    <template #footer>
      <button class="ui-btn ui-btn--ghost" @click="emit('close')">{{ result ? t('common.close') : t('common.cancel') }}</button>
      <button v-if="!result" class="ui-btn ui-btn--primary" :disabled="!canImport || saving" @click="submit">
        <span v-if="saving" class="ui-spinner" />
        {{ t('import.submit', { n: parsed.ok.length }) }}
      </button>
    </template>
  </BaseModal>
</template>

<style scoped>
.pick { display: flex; align-items: center; gap: .75rem; flex-wrap: wrap; }
.pick label { cursor: pointer; }
.link { background: none; color: var(--accent); font-size: .875rem; cursor: pointer; margin-left: auto; }
.section-label { font-size: .82rem; font-weight: 550; color: var(--text-sub); margin-bottom: .5rem; }
.map-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .5rem .75rem; }
@media (max-width: 640px) { .map-grid { grid-template-columns: 1fr 1fr; } }
.map-row { display: flex; flex-direction: column; gap: .25rem; font-size: .8rem; color: var(--text-sub); }
.map-row b { color: var(--red); }
.small { font-size: .82rem; }
</style>
