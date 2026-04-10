<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { api } from '@/services/api'

// ─── Props / Emits ────────────────────────────────────────────────────────────
const props = defineProps<{
  dataset: { id: string; name: string } | null
}>()
const emit = defineEmits<{ (e: 'close'): void }>()

// ─── State ────────────────────────────────────────────────────────────────────
const rows        = ref<Record<string, string>[]>([])
const columns     = ref<string[]>([])
const loading     = ref(false)
const saving      = ref(false)
const errorMsg    = ref<string | null>(null)
const successMsg  = ref<string | null>(null)

// editing
const editingCell = ref<{ row: number; col: string } | null>(null)
const editValue   = ref('')
const dirtyRows   = ref<Set<number>>(new Set())

// pagination
const page        = ref(1)
const PAGE_SIZE   = 20

const totalPages  = computed(() => Math.max(1, Math.ceil(rows.value.length / PAGE_SIZE)))
const visibleRows = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return rows.value.slice(start, start + PAGE_SIZE).map((r, i) => ({
    data: r,
    globalIndex: start + i
  }))
})

// ─── Load data ────────────────────────────────────────────────────────────────
watch(
  () => props.dataset,
  async (ds) => {
    if (!ds) { rows.value = []; columns.value = []; return }
    loading.value = true
    errorMsg.value = null
    dirtyRows.value = new Set()
    page.value = 1
    try {
      const res = await api.get(`/datasets/${ds.id}/rows`)
      columns.value = res.data.columns
      rows.value    = res.data.rows
    } catch {
      errorMsg.value = 'Αδυναμία φόρτωσης δεδομένων'
    } finally {
      loading.value = false
    }
  },
  { immediate: true }
)

// ─── Editing ──────────────────────────────────────────────────────────────────
const startEdit = (rowIndex: number, col: string) => {
  editingCell.value = { row: rowIndex, col }
  editValue.value   = rows.value[rowIndex]?.[col] ?? ''
}

const commitEdit = () => {
  if (!editingCell.value) return
  const { row, col } = editingCell.value
  if (rows.value[row]) {
    rows.value[row][col] = editValue.value
  }
  dirtyRows.value.add(row)
  editingCell.value = null
}

const cancelEdit = () => {
  editingCell.value = null
}

const isEditing = (rowIndex: number, col: string) =>
  editingCell.value?.row === rowIndex && editingCell.value?.col === col

// ─── Save ─────────────────────────────────────────────────────────────────────
const saveChanges = async () => {
  if (!props.dataset || dirtyRows.value.size === 0) return
  saving.value  = true
  errorMsg.value = null
  try {
    const changed = [...dirtyRows.value].map(i => ({ index: i, row: rows.value[i] }))
    await api.patch(`/datasets/${props.dataset.id}/rows`, { changes: changed })
    dirtyRows.value.clear()
    successMsg.value = 'Αποθηκεύτηκε!'
    setTimeout(() => (successMsg.value = null), 2500)
  } catch {
    errorMsg.value = 'Αποτυχία αποθήκευσης'
  } finally {
    saving.value = false
  }
}

// ─── Close ────────────────────────────────────────────────────────────────────
const close = () => {
  editingCell.value = null
  dirtyRows.value.clear()
  emit('close')
}
</script>

<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="dataset"
        class="modal-backdrop"
        @click.self="close"
      >
        <div class="modal-panel">

          <!-- ── Header ── -->
          <div class="modal-header">
            <div class="header-left">
              <span class="header-icon">📊</span>
              <div>
                <h2 class="modal-title">{{ dataset.name }}</h2>
                <p class="modal-subtitle">
                  {{ rows.length }} γραμμές · {{ columns.length }} στήλες
                  <span v-if="dirtyRows.size > 0" class="dirty-badge">
                    {{ dirtyRows.size }} αλλαγές
                  </span>
                </p>
              </div>
            </div>

            <div class="header-actions">
              <button
                v-if="dirtyRows.size > 0"
                class="btn-save"
                :disabled="saving"
                @click="saveChanges"
              >
                <span v-if="saving" class="spinner" />
                {{ saving ? 'Αποθήκευση…' : '💾 Αποθήκευση' }}
              </button>
              <button class="btn-close" @click="close">✕</button>
            </div>
          </div>

          <!-- ── Messages ── -->
          <div v-if="errorMsg"   class="msg msg-error">{{ errorMsg }}</div>
          <div v-if="successMsg" class="msg msg-success">✓ {{ successMsg }}</div>

          <!-- ── Body ── -->
          <div class="modal-body">

            <div v-if="loading" class="state-center">
              <div class="loader" />
              <p>Φόρτωση δεδομένων…</p>
            </div>

            <div v-else-if="rows.length === 0" class="state-center">
              <p class="text-muted">Δεν βρέθηκαν δεδομένα.</p>
            </div>

            <div v-else class="table-wrapper">
              <table class="data-table">
                <thead>
                  <tr>
                    <th class="th-index">#</th>
                    <th v-for="col in columns" :key="col">{{ col }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="{ data: row, globalIndex } in visibleRows"
                    :key="globalIndex"
                    :class="{ 'row-dirty': dirtyRows.has(globalIndex) }"
                  >
                    <td class="td-index">{{ globalIndex + 1 }}</td>

                    <td
                      v-for="col in columns"
                      :key="col"
                      class="td-cell"
                      @dblclick="startEdit(globalIndex, col)"
                    >
                      <!-- Editing input -->
                      <input
                        v-if="isEditing(globalIndex, col)"
                        v-model="editValue"
                        class="cell-input"
                        autofocus
                        @blur="commitEdit"
                        @keydown.enter="commitEdit"
                        @keydown.escape="cancelEdit"
                      />
                      <!-- Display value -->
                      <span v-else class="cell-value">
                        {{ row[col] ?? '' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- ── Footer / Pagination ── -->
          <div v-if="totalPages > 1" class="modal-footer">
            <button
              class="btn-page"
              :disabled="page === 1"
              @click="page--"
            >← Προηγ.</button>

            <span class="page-info">Σελίδα {{ page }} / {{ totalPages }}</span>

            <button
              class="btn-page"
              :disabled="page === totalPages"
              @click="page++"
            >Επόμ. →</button>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* ── Transitions ── */
.fade-enter-active, .fade-leave-active { transition: opacity .2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── Backdrop ── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

/* ── Panel ── */
.modal-panel {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 16px;
  width: 100%;
  max-width: 1100px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0,0,0,.6);
}

/* ── Header ── */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #1e293b;
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: .75rem; }
.header-icon { font-size: 1.5rem; }
.modal-title  { font-size: 1.1rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.modal-subtitle {
  font-size: .8rem; color: #64748b; margin: .15rem 0 0;
  display: flex; align-items: center; gap: .5rem;
}
.dirty-badge {
  background: #f59e0b22;
  color: #f59e0b;
  border: 1px solid #f59e0b55;
  border-radius: 999px;
  padding: .1rem .5rem;
  font-size: .72rem;
}

.header-actions { display: flex; align-items: center; gap: .75rem; }

.btn-save {
  display: flex; align-items: center; gap: .4rem;
  background: #22c55e;
  color: #0f172a;
  border: none;
  border-radius: 8px;
  padding: .45rem 1rem;
  font-size: .85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background .15s;
}
.btn-save:hover:not(:disabled) { background: #16a34a; }
.btn-save:disabled { opacity: .5; cursor: not-allowed; }

.btn-close {
  background: #1e293b;
  border: 1px solid #334155;
  color: #94a3b8;
  border-radius: 8px;
  width: 2rem; height: 2rem;
  cursor: pointer;
  font-size: .9rem;
  transition: background .15s, color .15s;
}
.btn-close:hover { background: #ef4444; color: white; border-color: #ef4444; }

/* ── Messages ── */
.msg {
  padding: .6rem 1.5rem;
  font-size: .85rem;
  flex-shrink: 0;
}
.msg-error   { background: #ef444415; color: #f87171; }
.msg-success { background: #22c55e15; color: #4ade80; }

/* ── Body ── */
.modal-body {
  flex: 1;
  overflow: hidden;
  position: relative;
}
.state-center {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  height: 200px; gap: 1rem; color: #475569;
}
.loader {
  width: 28px; height: 28px;
  border: 3px solid #1e293b;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Table ── */
.table-wrapper {
  overflow: auto;
  height: 100%;
  max-height: calc(90vh - 220px);
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: .82rem;
  color: #cbd5e1;
}
.data-table thead {
  position: sticky; top: 0; z-index: 1;
  background: #0f172a;
}
.data-table th {
  padding: .65rem 1rem;
  text-align: left;
  font-weight: 600;
  color: #64748b;
  border-bottom: 1px solid #1e293b;
  white-space: nowrap;
  font-size: .75rem;
  letter-spacing: .04em;
  text-transform: uppercase;
}
.th-index { width: 48px; color: #334155 !important; }

.data-table tbody tr {
  border-bottom: 1px solid #1e293b11;
  transition: background .1s;
}
.data-table tbody tr:hover { background: #1e293b55; }
.row-dirty { background: #f59e0b08 !important; }
.row-dirty:hover { background: #f59e0b12 !important; }

.td-index { color: #334155; text-align: center; font-variant-numeric: tabular-nums; }
.td-cell  { padding: .5rem 1rem; cursor: default; }

.cell-value {
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 220px;
}
.td-cell:hover .cell-value { color: #f1f5f9; }

.cell-input {
  background: #0f172a;
  border: 1px solid #4f46e5;
  border-radius: 4px;
  color: #f1f5f9;
  padding: .2rem .5rem;
  font-size: .82rem;
  width: 100%;
  min-width: 120px;
  outline: none;
  box-shadow: 0 0 0 2px #4f46e530;
}

/* ── Footer ── */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: .9rem 1.5rem;
  border-top: 1px solid #1e293b;
  flex-shrink: 0;
}
.btn-page {
  background: #1e293b;
  border: 1px solid #334155;
  color: #94a3b8;
  border-radius: 8px;
  padding: .35rem .9rem;
  font-size: .82rem;
  cursor: pointer;
  transition: background .15s;
}
.btn-page:hover:not(:disabled) { background: #334155; color: #f1f5f9; }
.btn-page:disabled { opacity: .35; cursor: not-allowed; }
.page-info { color: #64748b; font-size: .82rem; }

/* ── Spinner ── */
.spinner {
  width: 12px; height: 12px;
  border: 2px solid #0f172a44;
  border-top-color: #0f172a;
  border-radius: 50%;
  animation: spin .6s linear infinite;
  display: inline-block;
}
</style>