<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import DatasetPreviewModal from '@/views/DatasetPreviewModal.vue'

const authStore = useAuthStore()
const { t } = useI18n()

// ── Tab ────────────────────────────────────────────────────────────────────
const activeTab = ref<'datasets' | 'history'>('datasets')

// ── Datasets ───────────────────────────────────────────────────────────────
const datasets        = ref<any[]>([])
const loading         = ref(false)
const uploading       = ref(false)
const errorMsg        = ref<string | null>(null)
const selectedDataset = ref<any | null>(null)
const datasetToDelete = ref<any | null>(null)
const datasetToEdit   = ref<any | null>(null)
const editName        = ref('')
const openMenuId      = ref<string | null>(null)

const toggleMenu = (id: string) => { openMenuId.value = openMenuId.value === id ? null : id }
const closeMenu  = () => { openMenuId.value = null }

const loadDatasets = async () => {
  if (!authStore.currentBusiness?.id) return
  loading.value = true
  try {
    const res = await api.get('/datasets')
    datasets.value = res.data
  } catch {
    errorMsg.value = t('datasets.errorLoad')
  } finally {
    loading.value = false
  }
}

const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragging   = ref(false)

const triggerUpload = () => fileInputRef.value?.click()

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files?.[0]) await uploadFile(target.files[0])
  target.value = ''
}

const handleDrop = async (e: DragEvent) => {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) await uploadFile(file)
}

const uploadFile = async (file: File) => {
  if (!authStore.currentBusiness?.id) {
    errorMsg.value = t('datasets.errorNoBusiness')
    return
  }
  const formData = new FormData()
  formData.append('file', file)
  formData.append('business_id', authStore.currentBusiness.id)

  uploading.value = true
  errorMsg.value  = null
  try {
    await api.post('/datasets/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    await loadDatasets()
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || t('datasets.errorUpload')
  } finally {
    uploading.value = false
  }
}

const openPreview   = (d: any) => { selectedDataset.value = d; closeMenu() }
const confirmDelete = (d: any) => { datasetToDelete.value = d; closeMenu() }

const deleteConfirmed = async () => {
  if (!datasetToDelete.value) return
  try {
    await api.delete(`/datasets/${datasetToDelete.value.id}`)
    datasets.value = datasets.value.filter(d => d.id !== datasetToDelete.value.id)
  } catch {
    errorMsg.value = t('datasets.errorDelete')
  } finally {
    datasetToDelete.value = null
  }
}

const startEdit = (d: any) => { datasetToEdit.value = d; editName.value = d.name; closeMenu() }

const saveEdit = async () => {
  if (!datasetToEdit.value) return
  try {
    await api.patch(`/datasets/${datasetToEdit.value.id}`, { name: editName.value })
    datasetToEdit.value.name = editName.value
  } catch {
    errorMsg.value = t('datasets.errorSave')
  } finally {
    datasetToEdit.value = null
  }
}

// ── History ────────────────────────────────────────────────────────────────
const history     = ref<any[]>([])
const histLoading = ref(false)
const histFilter  = ref<'all' | 'sales_forecast'>('all')
const histLoaded  = ref(false)

const filteredHistory = computed(() =>
  histFilter.value === 'all'
    ? history.value
    : history.value.filter(h => h.type === histFilter.value)
)

const loadHistory = async () => {
  if (histLoaded.value) return
  histLoading.value = true
  try {
    const r = await api.get('/predictions')
    history.value = r.data
    histLoaded.value = true
  } catch {}
  histLoading.value = false
}

const switchTab = (tab: 'datasets' | 'history') => {
  activeTab.value = tab
  if (tab === 'history') loadHistory()
}

// ── Formatters ─────────────────────────────────────────────────────────────
const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString('el-GR', { day: '2-digit', month: 'short', year: 'numeric' })

const formatTime = (iso: string) =>
  new Date(iso).toLocaleTimeString('el-GR', { hour: '2-digit', minute: '2-digit' })

const fmtNum = (v: number) =>
  v?.toLocaleString('el-GR', { maximumFractionDigits: 2 }) ?? '—'

const fmtDateTime = (iso: string) =>
  new Date(iso).toLocaleString('el-GR', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })

onMounted(loadDatasets)
</script>

<template>
  <div class="page" @click="closeMenu">

    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <ellipse cx="12" cy="5" rx="9" ry="3"/>
            <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/>
            <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/>
          </svg>
        </div>
        <div>
          <h1 class="page-title">{{ t('nav.datasets') }}</h1>
          <p class="page-sub">{{ authStore.currentBusiness?.name }}</p>
        </div>
      </div>

      <button v-if="activeTab === 'datasets'" class="btn-upload" @click.stop="triggerUpload" :disabled="uploading">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        {{ uploading ? t('common.uploading') : t('datasets.uploadBtn') }}
      </button>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button class="tab" :class="{ active: activeTab === 'datasets' }" @click.stop="switchTab('datasets')">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <ellipse cx="12" cy="5" rx="9" ry="3"/>
          <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/>
          <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/>
        </svg>
        {{ t('datasets.tabs.datasets') }}
        <span class="tab-count">{{ datasets.length }}</span>
      </button>
      <button class="tab" :class="{ active: activeTab === 'history' }" @click.stop="switchTab('history')">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        {{ t('datasets.tabs.history') }}
        <span v-if="histLoaded" class="tab-count">{{ history.length }}</span>
      </button>
    </div>

    <!-- Error -->
    <Transition name="slide-down">
      <div v-if="errorMsg" class="error-bar" @click="errorMsg = null">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ errorMsg }}
        <span class="error-x">✕</span>
      </div>
    </Transition>

    <!-- DATASETS TAB -->
    <template v-if="activeTab === 'datasets'">

      <div
        class="drop-zone"
        :class="{ 'drop-zone--active': isDragging, 'drop-zone--busy': uploading }"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="handleDrop"
        @click.stop="triggerUpload"
      >
        <input ref="fileInputRef" type="file" accept=".csv" class="sr-only" @change="handleFileUpload" />
        <div class="drop-inner">
          <div class="drop-icon" :class="{ spin: uploading }">
            <svg v-if="!uploading" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="12" y1="18" x2="12" y2="12"/>
              <line x1="9" y1="15" x2="15" y2="15"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-dasharray="40" stroke-dashoffset="10"/>
            </svg>
          </div>
          <p class="drop-text">
            <span v-if="uploading">{{ t('common.uploading') }}</span>
            <span v-else-if="isDragging">{{ t('datasets.dropZone.active') }}</span>
            <span v-else>{{ t('datasets.dropZone.idle') }}</span>
          </p>
          <p class="drop-hint">{{ t('datasets.dropZone.hint') }}</p>
        </div>
      </div>

      <div class="card">
        <div v-if="loading" class="state">
          <div class="dots"><span/><span/><span/></div>
          <p>{{ t('common.loading') }}</p>
        </div>

        <div v-else-if="datasets.length === 0" class="state">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
            <ellipse cx="12" cy="5" rx="9" ry="3"/>
            <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/>
            <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/>
          </svg>
          <p class="state-title">{{ t('datasets.empty.title') }}</p>
          <p class="state-hint">{{ t('datasets.empty.hint') }}</p>
        </div>

        <table v-else class="table">
          <thead>
            <tr>
              <th>{{ t('datasets.table.filename') }}</th>
              <th>{{ t('datasets.table.date') }}</th>
              <th>{{ t('datasets.table.rows') }}</th>
              <th>{{ t('datasets.table.status') }}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(d, i) in datasets" :key="d.id" class="table-row" :style="{ animationDelay: `${i * 40}ms` }">
              <td>
                <div class="file-cell">
                  <div class="file-icon">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                    </svg>
                  </div>
                  <span class="file-name">{{ d.name }}</span>
                </div>
              </td>
              <td>
                <div class="date-cell">
                  <span>{{ formatDate(d.created_at) }}</span>
                  <span class="muted mono">{{ formatTime(d.created_at) }}</span>
                </div>
              </td>
              <td><span class="mono muted">{{ d.rows_count != null ? d.rows_count.toLocaleString('el-GR') : '—' }}</span></td>
              <td>
                <span class="badge badge--green">
                  <span class="badge-dot"/>
                  {{ d.status || 'uploaded' }}
                </span>
              </td>
              <td class="td-actions" @click.stop>
                <div class="menu-wrap">
                  <button class="btn-dots" @click.stop="toggleMenu(d.id)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/>
                    </svg>
                  </button>
                  <Transition name="menu-pop">
                    <div v-if="openMenuId === d.id" class="menu">
                      <button class="menu-item" @click="openPreview(d)">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                        {{ t('datasets.actions.preview') }}
                      </button>
                      <button class="menu-item" @click="startEdit(d)">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                        {{ t('datasets.actions.rename') }}
                      </button>
                      <div class="menu-sep"/>
                      <button class="menu-item menu-item--danger" @click="confirmDelete(d)">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                        {{ t('common.delete') }}
                      </button>
                    </div>
                  </Transition>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- HISTORY TAB -->
    <template v-else>
      <div class="hist-filters">
        <button class="fil-btn" :class="{ active: histFilter === 'all' }" @click.stop="histFilter = 'all'">{{ t('history.all') }}</button>
        <button class="fil-btn" :class="{ active: histFilter === 'sales_forecast' }" @click.stop="histFilter = 'sales_forecast'">Sales Forecast</button>
      </div>

      <div class="card">
        <div v-if="histLoading" class="state">
          <div class="dots"><span/><span/><span/></div>
          <p>{{ t('common.loading') }}</p>
        </div>

        <div v-else-if="filteredHistory.length === 0" class="state">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
          <p class="state-title">{{ t('history.empty') }}</p>
        </div>

        <div v-else class="hist-list">
          <div v-for="(h, i) in filteredHistory" :key="h.id" class="hist-item" :style="{ animationDelay: `${i * 40}ms` }">
            <div class="hist-icon">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
              </svg>
            </div>
            <div class="hist-info">
              <p class="hist-type">{{ h.type?.replace('_', ' ') ?? 'Prediction' }}</p>
              <p class="hist-date mono">{{ fmtDateTime(h.created_at) }}</p>
            </div>
            <div class="hist-tags">
              <span v-if="h.result?.summary" class="badge badge--teal">avg {{ fmtNum(h.result.summary.avg) }}</span>
              <span v-if="h.result?.summary?.total" class="badge badge--teal">{{ fmtNum(h.result.summary.total) }} total</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Preview Modal -->
    <DatasetPreviewModal :dataset="selectedDataset" @close="selectedDataset = null" />

    <!-- Delete Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="datasetToDelete" class="overlay" @click.self="datasetToDelete = null">
          <div class="dialog">
            <div class="dialog-icon dialog-icon--danger">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
                <path d="M10 11v6M14 11v6M9 6V4h6v2"/>
              </svg>
            </div>
            <h3 class="dialog-title">{{ t('datasets.delete.title') }}</h3>
            <p class="dialog-body">{{ t('datasets.delete.body', { name: datasetToDelete.name }) }}</p>
            <div class="dialog-actions">
              <button class="btn-ghost" @click="datasetToDelete = null">{{ t('common.cancel') }}</button>
              <button class="btn-danger" @click="deleteConfirmed">{{ t('common.delete') }}</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Rename Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="datasetToEdit" class="overlay" @click.self="datasetToEdit = null">
          <div class="dialog">
            <div class="dialog-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
            </div>
            <h3 class="dialog-title">{{ t('datasets.rename.title') }}</h3>
            <p class="dialog-body">{{ t('datasets.rename.body', { name: datasetToEdit.name }) }}</p>
            <input
              v-model="editName"
              class="dialog-input"
              :placeholder="t('datasets.rename.placeholder')"
              @keydown.enter="saveEdit"
              @keydown.escape="datasetToEdit = null"
              autofocus
            />
            <div class="dialog-actions">
              <button class="btn-ghost" @click="datasetToEdit = null">{{ t('common.cancel') }}</button>
              <button class="btn-primary" @click="saveEdit">{{ t('common.save') }}</button>
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
  gap: 1.25rem;
}

/* Header */
.page-header  { display: flex; align-items: center; justify-content: space-between; }
.header-left  { display: flex; align-items: center; gap: .85rem; }
.header-icon {
  width: 40px; height: 40px;
  background: rgba(46,196,182,.08);
  border: 1px solid rgba(46,196,182,.18);
  border-radius: var(--r-lg);
  display: flex; align-items: center; justify-content: center;
  color: var(--teal);
  flex-shrink: 0;
}
.page-title { font-size: 1.2rem; font-weight: 600; color: var(--text); margin: 0; letter-spacing: -.01em; }
.page-sub   { font-size: .73rem; color: var(--text-muted); margin: .12rem 0 0; }

.btn-upload {
  display: flex; align-items: center; gap: .4rem;
  background: rgba(46,196,182,.1);
  border: 1px solid rgba(46,196,182,.25);
  color: var(--teal);
  border-radius: var(--r);
  padding: .45rem .9rem;
  font-size: .8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background .15s, border-color .15s;
}
.btn-upload:hover:not(:disabled) { background: rgba(46,196,182,.18); }
.btn-upload:disabled { opacity: .4; cursor: not-allowed; }

/* Tabs */
.tabs {
  display: flex;
  gap: .25rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: .25rem;
  width: fit-content;
}
.tab {
  display: flex; align-items: center; gap: .4rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: .79rem;
  font-weight: 500;
  padding: .4rem .85rem;
  border-radius: var(--r);
  cursor: pointer;
  transition: background .15s, color .15s;
}
.tab.active { background: rgba(46,196,182,.1); color: var(--teal); }
.tab:hover:not(.active) { color: var(--text-sub); }

.tab-count {
  background: var(--border);
  color: var(--text-muted);
  font-size: .63rem;
  padding: .08rem .38rem;
  border-radius: 999px;
  min-width: 16px;
  text-align: center;
  font-variant-numeric: tabular-nums;
}
.tab.active .tab-count { background: rgba(46,196,182,.15); color: var(--teal-dim); }

/* Error */
.error-bar {
  display: flex; align-items: center; gap: .5rem;
  background: var(--red-bg);
  border: 1px solid rgba(224,85,85,.3);
  border-radius: var(--r);
  padding: .6rem .85rem;
  font-size: .79rem;
  color: var(--red);
  cursor: pointer;
}
.error-x { margin-left: auto; opacity: .5; }

/* Drop zone */
.drop-zone {
  border: 1.5px dashed var(--border-mid);
  border-radius: var(--r-lg);
  background: var(--bg-card);
  padding: 1.75rem;
  cursor: pointer;
  transition: border-color .2s, background .2s;
  text-align: center;
}
.drop-zone:hover, .drop-zone--active { border-color: var(--teal-dark); background: var(--bg-hover); }
.drop-zone--busy { pointer-events: none; opacity: .7; }

.drop-inner { display: flex; flex-direction: column; align-items: center; gap: .4rem; }
.drop-icon {
  width: 42px; height: 42px;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  display: flex; align-items: center; justify-content: center;
  color: var(--teal-dim);
  margin-bottom: .1rem;
}
.drop-icon.spin svg { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.sr-only   { display: none; }
.drop-text { font-size: .83rem; color: var(--text-sub); margin: 0; }
.drop-hint { font-size: .7rem; color: var(--text-muted); margin: 0; }

/* Card */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  overflow: hidden;
}

/* State */
.state {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: .6rem;
  padding: 3.5rem 2rem;
  color: var(--text-muted);
  font-size: .82rem;
}
.state-title { color: var(--text-sub); font-size: .86rem; font-weight: 500; margin: 0; }
.state-hint  { color: var(--text-muted); font-size: .73rem; margin: 0; }

.dots { display: flex; gap: .35rem; }
.dots span {
  width: 5px; height: 5px;
  background: var(--border-mid);
  border-radius: 50%;
  animation: pulse 1.2s ease-in-out infinite;
}
.dots span:nth-child(2) { animation-delay: .2s; }
.dots span:nth-child(3) { animation-delay: .4s; }
@keyframes pulse {
  0%, 80%, 100% { opacity: .2; transform: scale(.8); }
  40%           { opacity: 1;  transform: scale(1); }
}

/* Table */
.table { width: 100%; border-collapse: collapse; font-size: .81rem; }
.table thead tr { border-bottom: 1px solid var(--border); }
.table th {
  padding: .75rem 1.1rem;
  text-align: left;
  font-size: .67rem;
  font-weight: 600;
  letter-spacing: .07em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.table-row {
  border-bottom: 1px solid var(--border-light);
  animation: rowIn .3s ease both;
  transition: background .12s;
}
.table-row:last-child { border-bottom: none; }
.table-row:hover { background: var(--bg-hover); }
@keyframes rowIn {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}
.table td { padding: .8rem 1.1rem; vertical-align: middle; }

.file-cell { display: flex; align-items: center; gap: .55rem; }
.file-icon {
  width: 24px; height: 24px;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  color: var(--teal-dim);
  flex-shrink: 0;
}
.file-name {
  color: var(--text);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 230px;
}

.date-cell { display: flex; flex-direction: column; gap: .03rem; }
.mono  { font-variant-numeric: tabular-nums; letter-spacing: .01em; }
.muted { color: var(--text-muted); font-size: .72rem; }

/* Badges */
.badge {
  display: inline-flex; align-items: center; gap: .3rem;
  border-radius: 999px;
  padding: .2rem .6rem;
  font-size: .68rem;
  font-weight: 600;
  letter-spacing: .03em;
}
.badge--green { background: var(--green-bg); border: 1px solid rgba(58,184,122,.25); color: var(--green); }
.badge--teal  { background: rgba(46,196,182,.08); border: 1px solid rgba(46,196,182,.2); color: var(--teal-dim); }
.badge-dot    { width: 4px; height: 4px; background: var(--green); border-radius: 50%; }

/* Menu */
.td-actions { text-align: right; width: 42px; }
.menu-wrap  { position: relative; display: inline-block; }
.btn-dots {
  background: transparent; border: none; color: var(--text-muted);
  cursor: pointer; width: 26px; height: 26px;
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  transition: background .12s, color .12s;
}
.btn-dots:hover { background: var(--bg-hover); color: var(--text-sub); }

.menu {
  position: absolute; right: 0; top: calc(100% + 4px);
  background: var(--bg-card);
  border: 1px solid var(--border-mid);
  border-radius: var(--r-lg);
  padding: .25rem;
  min-width: 140px;
  z-index: 10;
  box-shadow: var(--shadow-lg);
}
.menu-item {
  display: flex; align-items: center; gap: .45rem;
  width: 100%; background: transparent; border: none;
  color: var(--text-sub);
  font-size: .78rem;
  padding: .42rem .6rem;
  border-radius: var(--r);
  cursor: pointer;
  transition: background .1s, color .1s;
  text-align: left;
}
.menu-item:hover         { background: var(--bg-hover); color: var(--text); }
.menu-item--danger       { color: var(--red); }
.menu-item--danger:hover { background: var(--red-bg); }
.menu-sep { height: 1px; background: var(--border); margin: .2rem 0; }

/* History */
.hist-filters { display: flex; gap: .3rem; }
.fil-btn {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: var(--r);
  padding: .38rem .8rem;
  font-size: .76rem;
  font-weight: 500;
  cursor: pointer;
  transition: all .15s;
}
.fil-btn.active { background: rgba(46,196,182,.1); border-color: rgba(46,196,182,.25); color: var(--teal); }
.fil-btn:hover:not(.active) { color: var(--text-sub); }

.hist-list { display: flex; flex-direction: column; gap: .35rem; padding: .65rem; }
.hist-item {
  display: flex; align-items: center; gap: .75rem;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: .75rem .9rem;
  transition: background .12s;
  animation: rowIn .3s ease both;
}
.hist-item:hover { background: var(--bg-hover); }
.hist-icon {
  width: 28px; height: 28px;
  background: rgba(46,196,182,.08);
  border: 1px solid rgba(46,196,182,.15);
  border-radius: var(--r);
  display: flex; align-items: center; justify-content: center;
  color: var(--teal);
  flex-shrink: 0;
}
.hist-info { flex: 1; }
.hist-type { font-size: .8rem; font-weight: 500; color: var(--text-sub); margin: 0; text-transform: capitalize; }
.hist-date { font-size: .67rem; color: var(--text-muted); margin: .05rem 0 0; }
.hist-tags { display: flex; gap: .3rem; flex-wrap: wrap; }

/* Dialogs */
.overlay {
  position: fixed; inset: 0; z-index: 50;
  background: rgba(0,0,0,.65);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  padding: 1rem;
}
.dialog {
  background: var(--bg-card);
  border: 1px solid var(--border-mid);
  border-radius: var(--r-xl);
  padding: 1.65rem;
  width: 100%; max-width: 390px;
  box-shadow: var(--shadow-lg);
  display: flex; flex-direction: column; gap: .85rem;
}
.dialog-icon {
  width: 38px; height: 38px;
  background: rgba(46,196,182,.08);
  border: 1px solid rgba(46,196,182,.18);
  border-radius: var(--r-lg);
  display: flex; align-items: center; justify-content: center;
  color: var(--teal);
}
.dialog-icon--danger { background: var(--red-bg); border-color: rgba(224,85,85,.3); color: var(--red); }
.dialog-title { font-size: .92rem; font-weight: 600; color: var(--text); margin: 0; }
.dialog-body  { font-size: .8rem; color: var(--text-sub); margin: 0; line-height: 1.6; }
.dialog-body strong { color: var(--text); }

.dialog-input {
  background: var(--bg);
  border: 1px solid var(--border-mid);
  border-radius: var(--r);
  color: var(--text);
  padding: .55rem .8rem;
  font-size: .82rem;
  outline: none;
  transition: border-color .15s;
}
.dialog-input:focus { border-color: var(--teal-dark); box-shadow: 0 0 0 3px rgba(46,196,182,.12); }

.dialog-actions { display: flex; justify-content: flex-end; gap: .6rem; }

.btn-ghost {
  background: transparent; border: 1px solid var(--border-mid); color: var(--text-sub);
  border-radius: var(--r); padding: .42rem .9rem; font-size: .79rem; cursor: pointer;
  transition: border-color .15s, color .15s;
}
.btn-ghost:hover { border-color: var(--border-mid); color: var(--text); }

.btn-primary {
  background: rgba(46,196,182,.12); border: 1px solid rgba(46,196,182,.3); color: var(--teal);
  border-radius: var(--r); padding: .42rem .9rem; font-size: .79rem; font-weight: 600; cursor: pointer;
  transition: background .15s;
}
.btn-primary:hover { background: rgba(46,196,182,.2); }

.btn-danger {
  background: var(--red-bg); border: 1px solid rgba(224,85,85,.3); color: var(--red);
  border-radius: var(--r); padding: .42rem .9rem; font-size: .79rem; font-weight: 600; cursor: pointer;
  transition: background .15s;
}
.btn-danger:hover { background: rgba(224,85,85,.2); }

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }

.slide-down-enter-active { transition: all .2s ease; }
.slide-down-leave-active { transition: all .15s ease; }
.slide-down-enter-from   { opacity: 0; transform: translateY(-6px); }
.slide-down-leave-to     { opacity: 0; transform: translateY(-4px); }

.menu-pop-enter-active { transition: all .13s cubic-bezier(.2,.8,.3,1); }
.menu-pop-leave-active { transition: all .09s ease; }
.menu-pop-enter-from   { opacity: 0; transform: scale(.93) translateY(-4px); }
.menu-pop-leave-to     { opacity: 0; transform: scale(.96); }
</style>
