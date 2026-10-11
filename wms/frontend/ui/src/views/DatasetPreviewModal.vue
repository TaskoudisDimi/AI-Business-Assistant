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
              <div class="header-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <ellipse cx="12" cy="5" rx="9" ry="3"/>
                  <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/>
                  <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/>
                </svg>
              </div>
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
                {{ saving ? 'Αποθήκευση…' : 'Αποθήκευση' }}
              </button>
              <button class="btn-close" @click="close">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
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
.fade-enter-active, .fade-leave-active { transition: opacity .2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.modal-backdrop {
  position: fixed; inset: 0; z-index: 50;
  background: rgba(0, 0, 0, .65);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  padding: 1rem;
}

.modal-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-mid);
  border-radius: var(--r-xl);
  width: 100%; max-width: 1100px; max-height: 90vh;
  display: flex; flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

/* Header */
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: .75rem; }
.header-icon {
  width: 36px; height: 36px;
  background: rgba(62, 207, 191, .08);
  border: 1px solid rgba(62, 207, 191, .18);
  border-radius: var(--r-lg);
  display: flex; align-items: center; justify-content: center;
  color: var(--teal);
  flex-shrink: 0;
}
.modal-title    { font-size: .95rem; font-weight: 600; color: var(--text); margin: 0; letter-spacing: -.01em; }
.modal-subtitle { font-size: .73rem; color: var(--text-muted); margin: .12rem 0 0; display: flex; align-items: center; gap: .5rem; }
.dirty-badge {
  background: rgba(212,160,23,.1); color: var(--amber);
  border: 1px solid rgba(212,160,23,.25);
  border-radius: 999px; padding: .08rem .5rem; font-size: .67rem; font-weight: 600;
}

.header-actions { display: flex; align-items: center; gap: .6rem; }

.btn-save {
  display: flex; align-items: center; gap: .4rem;
  background: rgba(58,184,122,.12); border: 1px solid rgba(58,184,122,.3); color: var(--green);
  border-radius: var(--r); padding: .42rem .9rem;
  font-size: .79rem; font-weight: 600; cursor: pointer; transition: background .15s;
}
.btn-save:hover:not(:disabled) { background: rgba(58,184,122,.2); }
.btn-save:disabled { opacity: .4; cursor: not-allowed; }

.btn-close {
  background: var(--bg-hover); border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: var(--r); width: 30px; height: 30px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: background .15s, color .15s, border-color .15s;
}
.btn-close:hover { background: var(--red-bg); border-color: rgba(224,85,85,.3); color: var(--red); }

/* Messages */
.msg { padding: .55rem 1.5rem; font-size: .8rem; flex-shrink: 0; }
.msg-error   { background: var(--red-bg);   color: var(--red);   border-bottom: 1px solid rgba(224,85,85,.2); }
.msg-success { background: var(--green-bg); color: var(--green); border-bottom: 1px solid rgba(58,184,122,.2); }

/* Body */
.modal-body { flex: 1; overflow: hidden; position: relative; }
.state-center {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  height: 200px; gap: 1rem; color: var(--text-muted); font-size: .82rem;
}
.text-muted { color: var(--text-muted); }
.loader {
  width: 26px; height: 26px;
  border: 2px solid var(--border-mid); border-top-color: var(--teal);
  border-radius: 50%; animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Table */
.table-wrapper { overflow: auto; height: 100%; max-height: calc(90vh - 210px); }
.data-table { width: 100%; border-collapse: collapse; font-size: .82rem; color: var(--text); }
.data-table thead { position: sticky; top: 0; z-index: 1; background: var(--bg-card); }
.data-table th {
  padding: .6rem 1rem; text-align: left; font-weight: 600;
  color: var(--text-muted); border-bottom: 1px solid var(--border);
  white-space: nowrap; font-size: .67rem; letter-spacing: .06em; text-transform: uppercase;
}
.th-index { width: 48px; }
.data-table tbody tr { border-bottom: 1px solid var(--border-light); transition: background .1s; }
.data-table tbody tr:hover { background: var(--bg-hover); }
.row-dirty { background: rgba(212,160,23,.04) !important; }
.row-dirty:hover { background: rgba(212,160,23,.08) !important; }

.td-index { color: var(--text-muted); text-align: center; font-variant-numeric: tabular-nums; }
.td-cell  { padding: .5rem 1rem; cursor: default; }
.cell-value { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 220px; color: var(--text-sub); }
.td-cell:hover .cell-value { color: var(--text); }

.cell-input {
  background: var(--bg-input); border: 1px solid var(--teal-dark);
  border-radius: var(--r); color: var(--text);
  padding: .2rem .5rem; font-size: .82rem; width: 100%; min-width: 120px;
  outline: none; box-shadow: 0 0 0 3px var(--teal-glow);
}

/* Footer */
.modal-footer {
  display: flex; align-items: center; justify-content: center; gap: 1rem;
  padding: .85rem 1.5rem;
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}
.btn-page {
  background: var(--bg-hover); border: 1px solid var(--border); color: var(--text-muted);
  border-radius: var(--r); padding: .35rem .9rem;
  font-size: .79rem; cursor: pointer; transition: background .15s, color .15s, border-color .15s;
}
.btn-page:hover:not(:disabled) { border-color: var(--border-mid); color: var(--text); }
.btn-page:disabled { opacity: .35; cursor: not-allowed; }
.page-info { color: var(--text-muted); font-size: .79rem; font-variant-numeric: tabular-nums; }

.spinner {
  width: 12px; height: 12px; border-radius: 50%;
  border: 2px solid transparent; border-top-color: currentColor;
  animation: spin .6s linear infinite; display: inline-block;
}
</style>