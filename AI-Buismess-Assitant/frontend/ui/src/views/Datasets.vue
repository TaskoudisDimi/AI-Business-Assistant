<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import DatasetPreviewModal from '@/views/DatasetPreviewModal.vue'

const authStore = useAuthStore()

const datasets = ref<any[]>([])
const loading = ref(false)
const uploading = ref(false)
const errorMsg = ref<string | null>(null)

const selectedDataset = ref<any | null>(null)
const datasetToDelete = ref<any | null>(null)
const datasetToEdit = ref<any | null>(null)
const editName = ref('')

const openMenuId = ref<string | null>(null)
const toggleMenu = (id: string) => {
  openMenuId.value = openMenuId.value === id ? null : id
}
const closeMenu = () => { openMenuId.value = null }

// ================= LOAD =================
const loadDatasets = async () => {
  if (!authStore.currentBusiness?.id) return
  loading.value = true
  try {
    const res = await api.get('/datasets')
    datasets.value = res.data
  } catch (err) {
    errorMsg.value = 'Αδυναμία φόρτωσης datasets'
  } finally {
    loading.value = false
  }
}

// ================= UPLOAD =================
const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)

const triggerUpload = () => fileInputRef.value?.click()

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files?.length) return
  if (target.files[0]) {
    await uploadFile(target.files[0])
  }
  target.value = ''
}

const handleDrop = async (e: DragEvent) => {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (!file) return
  await uploadFile(file)
}

const uploadFile = async (file: File) => {
  if (!authStore.currentBusiness?.id) {
    errorMsg.value = 'Δεν έχει επιλεγεί επιχείρηση'
    return
  }
  const formData = new FormData()
  formData.append('file', file)
  formData.append('business_id', authStore.currentBusiness.id)

  uploading.value = true
  errorMsg.value = null
  try {
    await api.post('/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    await loadDatasets()
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || 'Αποτυχία upload'
  } finally {
    uploading.value = false
  }
}

// ================= ACTIONS =================
const openPreview = (dataset: any) => {
  selectedDataset.value = dataset
  closeMenu()
}

const confirmDelete = (dataset: any) => {
  datasetToDelete.value = dataset
  closeMenu()
}

const deleteConfirmed = async () => {
  if (!datasetToDelete.value) return
  try {
    await api.delete(`/datasets/${datasetToDelete.value.id}`)
    datasets.value = datasets.value.filter(d => d.id !== datasetToDelete.value.id)
  } catch {
    errorMsg.value = 'Αποτυχία διαγραφής'
  } finally {
    datasetToDelete.value = null
  }
}

const startEdit = (dataset: any) => {
  datasetToEdit.value = dataset
  editName.value = dataset.name
  closeMenu()
}

const saveEdit = async () => {
  if (!datasetToEdit.value) return
  try {
    await api.patch(`/datasets/${datasetToEdit.value.id}`, { name: editName.value })
    datasetToEdit.value.name = editName.value
  } catch {
    errorMsg.value = 'Αποτυχία αποθήκευσης'
  } finally {
    datasetToEdit.value = null
  }
}

const formatDate = (iso: string) => {
  const d = new Date(iso)
  return d.toLocaleDateString('el-GR', { day: '2-digit', month: 'short', year: 'numeric' })
}

const formatTime = (iso: string) => {
  return new Date(iso).toLocaleTimeString('el-GR', { hour: '2-digit', minute: '2-digit' })
}

onMounted(loadDatasets)
</script>

<template>
  <div class="ds-page" @click="closeMenu">

    <!-- ── Header ── -->
    <div class="ds-header">
      <div class="ds-header-left">
        <div class="ds-icon-wrap">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/>
            <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/>
          </svg>
        </div>
        <div>
          <h1 class="ds-title">Datasets</h1>
          <p class="ds-subtitle">{{ datasets.length }} αρχεί{{ datasets.length === 1 ? 'ο' : 'α' }} · {{ authStore.currentBusiness?.name }}</p>
        </div>
      </div>

      <button class="btn-upload-top" @click.stop="triggerUpload" :disabled="uploading">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        {{ uploading ? 'Ανέβασμα…' : 'Upload' }}
      </button>
    </div>

    <!-- ── Error ── -->
    <Transition name="slide-down">
      <div v-if="errorMsg" class="ds-error" @click="errorMsg = null">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ errorMsg }}
        <span class="error-dismiss">✕</span>
      </div>
    </Transition>

    <!-- ── Drop Zone ── -->
    <div
      class="drop-zone"
      :class="{ 'drop-zone--active': isDragging, 'drop-zone--uploading': uploading }"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="handleDrop"
      @click.stop="triggerUpload"
    >
      <input
        ref="fileInputRef"
        type="file"
        accept=".csv"
        class="hidden-input"
        @change="handleFileUpload"
      />

      <div class="drop-zone-inner">
        <div class="drop-icon" :class="{ spin: uploading }">
          <svg v-if="!uploading" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>
            <line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/>
          </svg>
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-dasharray="40" stroke-dashoffset="10"/>
          </svg>
        </div>
        <p class="drop-text">
          <span v-if="uploading">Ανέβασμα αρχείου…</span>
          <span v-else-if="isDragging">Άσε το αρχείο εδώ</span>
          <span v-else>Drag & drop CSV <em>ή</em> κλικ για επιλογή</span>
        </p>
        <p class="drop-hint">Υποστηρίζονται .csv αρχεία</p>
      </div>
    </div>

    <!-- ── Table Card ── -->
    <div class="ds-card">

      <!-- Loading -->
      <div v-if="loading" class="ds-state">
        <div class="pulse-dots"><span/><span/><span/></div>
        <p>Φόρτωση datasets…</p>
      </div>

      <!-- Empty -->
      <div v-else-if="datasets.length === 0" class="ds-state">
        <div class="empty-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
            <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/>
            <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/>
          </svg>
        </div>
        <p class="empty-title">Κανένα dataset ακόμα</p>
        <p class="empty-hint">Ανέβασε ένα CSV για να ξεκινήσεις</p>
      </div>

      <!-- Table -->
      <div v-else class="ds-table-wrap">
        <table class="ds-table">
          <thead>
            <tr>
              <th>Όνομα αρχείου</th>
              <th>Ημερομηνία</th>
              <th>Γραμμές</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(d, i) in datasets"
              :key="d.id"
              class="ds-row"
              :style="{ animationDelay: `${i * 40}ms` }"
            >
              <!-- Name -->
              <td>
                <div class="file-cell">
                  <div class="file-icon">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>
                    </svg>
                  </div>
                  <span class="file-name">{{ d.name }}</span>
                </div>
              </td>

              <!-- Date -->
              <td>
                <div class="date-cell">
                  <span class="date-main">{{ formatDate(d.created_at) }}</span>
                  <span class="date-time">{{ formatTime(d.created_at) }}</span>
                </div>
              </td>

              <!-- Rows -->
              <td>
                <span class="rows-count">{{ d.rows_count != null ? d.rows_count.toLocaleString('el-GR') : '—' }}</span>
              </td>

              <!-- Status -->
              <td>
                <span class="status-badge">
                  <span class="status-dot" />
                  {{ d.status || 'uploaded' }}
                </span>
              </td>

              <!-- Actions -->
              <td class="td-actions" @click.stop>
                <div class="action-menu-wrap">
                  <button class="btn-dots" @click.stop="toggleMenu(d.id)">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                      <circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/>
                    </svg>
                  </button>

                  <Transition name="menu-pop">
                    <div v-if="openMenuId === d.id" class="action-menu">
                      <button class="menu-item" @click="openPreview(d)">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                        Προβολή
                      </button>
                      <button class="menu-item" @click="startEdit(d)">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                        Μετονομασία
                      </button>
                      <div class="menu-divider" />
                      <button class="menu-item menu-item--danger" @click="confirmDelete(d)">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                        Διαγραφή
                      </button>
                    </div>
                  </Transition>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── Preview Modal ── -->
    <DatasetPreviewModal
      :dataset="selectedDataset"
      @close="selectedDataset = null"
    />

    <!-- ── Delete Modal ── -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="datasetToDelete" class="overlay" @click.self="datasetToDelete = null">
          <div class="dialog">
            <div class="dialog-icon dialog-icon--danger">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
            </div>
            <h3 class="dialog-title">Διαγραφή Dataset</h3>
            <p class="dialog-body">
              Σίγουρα θέλεις να διαγράψεις το
              <strong>{{ datasetToDelete.name }}</strong>;
              Η ενέργεια δεν αναιρείται.
            </p>
            <div class="dialog-actions">
              <button class="btn-ghost" @click="datasetToDelete = null">Άκυρο</button>
              <button class="btn-danger" @click="deleteConfirmed">Διαγραφή</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Edit Modal ── -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="datasetToEdit" class="overlay" @click.self="datasetToEdit = null">
          <div class="dialog">
            <div class="dialog-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </div>
            <h3 class="dialog-title">Μετονομασία</h3>
            <p class="dialog-body">Νέο όνομα για το <strong>{{ datasetToEdit.name }}</strong></p>
            <input
              v-model="editName"
              class="dialog-input"
              placeholder="Όνομα dataset…"
              @keydown.enter="saveEdit"
              @keydown.escape="datasetToEdit = null"
              autofocus
            />
            <div class="dialog-actions">
              <button class="btn-ghost" @click="datasetToEdit = null">Άκυρο</button>
              <button class="btn-primary" @click="saveEdit">Αποθήκευση</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<style scoped>
/* ── Imports ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@400;500;600;700&display=swap');

/* ── Root ── */
.ds-page {
  min-height: 100vh;
  padding: 2rem 2.5rem;
  background: #080d16;
  font-family: 'Sora', sans-serif;
  color: #c8d6e8;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ── Header ── */
.ds-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.ds-header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.ds-icon-wrap {
  width: 44px; height: 44px;
  background: linear-gradient(135deg, #1a2640 0%, #0e1a2e 100%);
  border: 1px solid #1e3050;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #4a9eff;
}
.ds-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #e8f0fe;
  margin: 0;
  letter-spacing: -.02em;
}
.ds-subtitle {
  font-size: .78rem;
  color: #3d5570;
  margin: .1rem 0 0;
  font-family: 'DM Mono', monospace;
}

.btn-upload-top {
  display: flex; align-items: center; gap: .5rem;
  background: #1a3460;
  border: 1px solid #2a4a7a;
  color: #7ab8ff;
  border-radius: 10px;
  padding: .55rem 1.1rem;
  font-size: .82rem;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Sora', sans-serif;
  transition: background .15s, border-color .15s, color .15s;
}
.btn-upload-top:hover:not(:disabled) {
  background: #22448a;
  border-color: #3a5faa;
  color: #aad4ff;
}
.btn-upload-top:disabled { opacity: .4; cursor: not-allowed; }

/* ── Error ── */
.ds-error {
  display: flex; align-items: center; gap: .6rem;
  background: #1f0a0a;
  border: 1px solid #3d1515;
  border-radius: 10px;
  padding: .7rem 1rem;
  font-size: .82rem;
  color: #f07070;
  cursor: pointer;
}
.error-dismiss { margin-left: auto; opacity: .5; }

/* ── Drop Zone ── */
.drop-zone {
  border: 1.5px dashed #1e3050;
  border-radius: 14px;
  background: #0a1220;
  padding: 2rem;
  cursor: pointer;
  transition: border-color .2s, background .2s;
  text-align: center;
}
.drop-zone:hover,
.drop-zone--active {
  border-color: #2a5299;
  background: #0d1a30;
}
.drop-zone--uploading {
  border-color: #1d4a8a;
  pointer-events: none;
}
.drop-zone-inner {
  display: flex; flex-direction: column; align-items: center; gap: .5rem;
}
.drop-icon {
  width: 48px; height: 48px;
  background: #0e1a2e;
  border: 1px solid #1e3050;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #3a6fcc;
  margin-bottom: .25rem;
}
.drop-icon.spin svg {
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.hidden-input { display: none; }

.drop-text {
  font-size: .88rem; color: #6a8aac; margin: 0;
}
.drop-text em { font-style: normal; color: #3a6fcc; }
.drop-hint { font-size: .75rem; color: #2a4060; margin: 0; font-family: 'DM Mono', monospace; }

/* ── Card ── */
.ds-card {
  background: #0a1220;
  border: 1px solid #111e33;
  border-radius: 16px;
  overflow: hidden;
}

/* ── States ── */
.ds-state {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: .75rem;
  padding: 4rem 2rem;
  color: #2a4060;
  font-size: .85rem;
}
.pulse-dots {
  display: flex; gap: .4rem;
}
.pulse-dots span {
  width: 6px; height: 6px;
  background: #2a4a7a;
  border-radius: 50%;
  animation: pulse 1.2s ease-in-out infinite;
}
.pulse-dots span:nth-child(2) { animation-delay: .2s; }
.pulse-dots span:nth-child(3) { animation-delay: .4s; }
@keyframes pulse {
  0%, 80%, 100% { opacity: .2; transform: scale(.8); }
  40% { opacity: 1; transform: scale(1); }
}

.empty-icon { color: #1e3050; margin-bottom: .25rem; }
.empty-title { color: #3a5570; font-size: .9rem; font-weight: 600; margin: 0; }
.empty-hint  { color: #243040; font-size: .78rem; margin: 0; }

/* ── Table ── */
.ds-table-wrap { overflow-x: auto; }
.ds-table {
  width: 100%;
  border-collapse: collapse;
  font-size: .83rem;
}
.ds-table thead tr {
  border-bottom: 1px solid #111e33;
}
.ds-table th {
  padding: .85rem 1.25rem;
  text-align: left;
  font-size: .7rem;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: #2a4060;
  font-family: 'DM Mono', monospace;
}

.ds-row {
  border-bottom: 1px solid #0d1828;
  animation: rowIn .3s ease both;
  transition: background .12s;
}
@keyframes rowIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.ds-row:last-child { border-bottom: none; }
.ds-row:hover { background: #0e1f38; }

.ds-table td {
  padding: .9rem 1.25rem;
  vertical-align: middle;
}

/* File cell */
.file-cell { display: flex; align-items: center; gap: .65rem; }
.file-icon {
  width: 28px; height: 28px;
  background: #0d1828;
  border: 1px solid #162035;
  border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  color: #2a5299;
  flex-shrink: 0;
}
.file-name {
  color: #b8d0ec;
  font-weight: 500;
  font-size: .84rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 260px;
}

/* Date cell */
.date-cell { display: flex; flex-direction: column; gap: .1rem; }
.date-main { color: #7a9cc0; font-size: .82rem; }
.date-time { color: #2a4060; font-size: .72rem; font-family: 'DM Mono', monospace; }

/* Rows count */
.rows-count {
  font-family: 'DM Mono', monospace;
  font-size: .8rem;
  color: #3a6080;
}

/* Status badge */
.status-badge {
  display: inline-flex; align-items: center; gap: .4rem;
  background: #0d2a1a;
  border: 1px solid #1a4a30;
  color: #3a9a60;
  border-radius: 999px;
  padding: .25rem .75rem;
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .04em;
  font-family: 'DM Mono', monospace;
}
.status-dot {
  width: 5px; height: 5px;
  background: #3a9a60;
  border-radius: 50%;
  box-shadow: 0 0 6px #3a9a60;
}

/* ── Action Menu ── */
.td-actions { text-align: right; width: 48px; }
.action-menu-wrap { position: relative; display: inline-block; }

.btn-dots {
  background: transparent;
  border: none;
  color: #2a4060;
  cursor: pointer;
  width: 30px; height: 30px;
  border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  transition: background .12s, color .12s;
}
.btn-dots:hover { background: #111e33; color: #7a9cc0; }

.action-menu {
  position: absolute;
  right: 0; top: calc(100% + 6px);
  background: #0a1525;
  border: 1px solid #162035;
  border-radius: 10px;
  padding: .35rem;
  min-width: 150px;
  z-index: 10;
  box-shadow: 0 12px 30px rgba(0,0,0,.5);
}
.menu-item {
  display: flex; align-items: center; gap: .55rem;
  width: 100%;
  background: transparent;
  border: none;
  color: #7a9cc0;
  font-size: .8rem;
  font-family: 'Sora', sans-serif;
  padding: .5rem .7rem;
  border-radius: 7px;
  cursor: pointer;
  transition: background .1s, color .1s;
  text-align: left;
}
.menu-item:hover { background: #111e33; color: #b8d0ec; }
.menu-item--danger { color: #8a3030; }
.menu-item--danger:hover { background: #1a0a0a; color: #f07070; }
.menu-divider { height: 1px; background: #111e33; margin: .25rem 0; }

/* ── Dialogs ── */
.overlay {
  position: fixed; inset: 0; z-index: 50;
  background: rgba(0, 5, 15, .75);
  backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center;
  padding: 1rem;
}
.dialog {
  background: #0a1525;
  border: 1px solid #162035;
  border-radius: 16px;
  padding: 2rem;
  width: 100%; max-width: 420px;
  box-shadow: 0 30px 60px rgba(0,0,0,.6);
  display: flex; flex-direction: column; gap: 1rem;
}
.dialog-icon {
  width: 44px; height: 44px;
  background: #0d1f38;
  border: 1px solid #162a48;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #4a9eff;
}
.dialog-icon--danger {
  background: #1a0a0a;
  border-color: #3d1515;
  color: #cc5050;
}
.dialog-title {
  font-size: 1rem; font-weight: 700;
  color: #e8f0fe; margin: 0;
}
.dialog-body {
  font-size: .83rem; color: #4a6a8a; margin: 0; line-height: 1.6;
}
.dialog-body strong { color: #7a9cc0; }

.dialog-input {
  background: #080d16;
  border: 1px solid #162035;
  border-radius: 9px;
  color: #c8d6e8;
  padding: .65rem .9rem;
  font-size: .85rem;
  font-family: 'Sora', sans-serif;
  outline: none;
  transition: border-color .15s;
}
.dialog-input:focus { border-color: #2a5299; box-shadow: 0 0 0 3px #2a529922; }

.dialog-actions {
  display: flex; justify-content: flex-end; gap: .75rem;
}
.btn-ghost {
  background: transparent;
  border: 1px solid #162035;
  color: #4a6a8a;
  border-radius: 9px;
  padding: .5rem 1.1rem;
  font-size: .82rem;
  font-family: 'Sora', sans-serif;
  cursor: pointer;
  transition: border-color .15s, color .15s;
}
.btn-ghost:hover { border-color: #2a4060; color: #7a9cc0; }

.btn-primary {
  background: #1a3460;
  border: 1px solid #2a4a7a;
  color: #7ab8ff;
  border-radius: 9px;
  padding: .5rem 1.1rem;
  font-size: .82rem;
  font-family: 'Sora', sans-serif;
  cursor: pointer;
  font-weight: 600;
  transition: background .15s;
}
.btn-primary:hover { background: #22448a; }

.btn-danger {
  background: #3d1515;
  border: 1px solid #5a2020;
  color: #f07070;
  border-radius: 9px;
  padding: .5rem 1.1rem;
  font-size: .82rem;
  font-family: 'Sora', sans-serif;
  cursor: pointer;
  font-weight: 600;
  transition: background .15s;
}
.btn-danger:hover { background: #5a1a1a; }

/* ── Transitions ── */
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-down-enter-active { transition: all .2s ease; }
.slide-down-leave-active { transition: all .15s ease; }
.slide-down-enter-from { opacity: 0; transform: translateY(-8px); }
.slide-down-leave-to   { opacity: 0; transform: translateY(-4px); }

.menu-pop-enter-active { transition: all .15s cubic-bezier(.2,.8,.3,1); }
.menu-pop-leave-active { transition: all .1s ease; }
.menu-pop-enter-from { opacity: 0; transform: scale(.92) translateY(-6px); }
.menu-pop-leave-to   { opacity: 0; transform: scale(.95); }
</style>