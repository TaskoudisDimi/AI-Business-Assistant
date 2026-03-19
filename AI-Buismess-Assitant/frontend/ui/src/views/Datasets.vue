<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const datasets = ref<any[]>([])
const uploading = ref(false)
const errorMsg = ref<string | null>(null)
const loading = ref(false)
const selectedDataset = ref<any | null>(null)  // για preview
const previewData = ref<any[]>([])             // rows του CSV
const previewLoading = ref(false)
const editName = ref<string>('')

// Φόρτωση datasets
const loadDatasets = async () => {
  if (!authStore.currentBusiness?.id) return
  loading.value = true
  try {
    const res = await api.get('/datasets')
    datasets.value = res.data
  } catch (err) {
    console.error(err)
    errorMsg.value = 'Αδυναμία φόρτωσης datasets'
  } finally {
    loading.value = false
  }
}

// Upload
const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files?.length) return

  const file = target.files[0]!

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
    const res = await api.post('/datasets/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    // Αυτόματα refresh λίστας
    await loadDatasets()

  } catch (err: any) {
    console.error(err)
    errorMsg.value = err.response?.data?.detail || 'Αποτυχία upload'
  } finally {
    uploading.value = false
    target.value = ''
  }
}

// Delete
const deleteDataset = async (id: string) => {
  if (!confirm('Σίγουρα θέλεις να διαγράψεις αυτό το dataset;')) return

  try {
    await api.delete(`/datasets/${id}`)
    datasets.value = datasets.value.filter(d => d.id !== id)
    if (selectedDataset.value?.id === id) {
      selectedDataset.value = null
      previewData.value = []
    }
  } catch (err) {
    errorMsg.value = 'Αποτυχία διαγραφής'
  }
}

const openPreview = async (dataset: any) => {
  selectedDataset.value = dataset
  previewLoading.value = true
  previewData.value = []

  try {
    const signed = await api.get(`/datasets/signed-url/${dataset.id}`)
    const url = signed.data.signed_url

    const res = await fetch(url)
    const text = await res.text()
    const lines = text.split('\n').filter(l => l.trim())
    const headers = lines[0]?.split(',') || []

    previewData.value = lines.slice(1, 11).map(line => {  
      const values = line.split(',')
      return headers.reduce((obj, h, i) => {
        obj[h.trim()] = values[i]?.trim()
        return obj
      }, {} as any)
    })
  } catch (err) {
    console.error(err)
    errorMsg.value = 'Αδυναμία φόρτωσης δεδομένων'
  } finally {
    previewLoading.value = false
  }
}

const startEdit = (dataset: any) => {
  editName.value = dataset.name
  dataset.isEditing = true
}

const saveEdit = async (dataset: any) => {
  try {
    await api.patch(`/datasets/${dataset.id}`, { name: editName.value })
    dataset.name = editName.value
    dataset.isEditing = false
  } catch (err) {
    errorMsg.value = 'Αποτυχία αποθήκευσης ονόματος'
  }
}

onMounted(() => {
  loadDatasets()
})
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">Datasets</h1>

    <div class="mb-8">
      <input
        type="file"
        accept=".csv"
        @change="handleFileUpload"
        class="file-input file-input-bordered w-full max-w-xs"
      />
      <p v-if="uploading" class="text-info mt-2">Ανέβασμα...</p>
      <p v-if="errorMsg" class="text-error mt-2">{{ errorMsg }}</p>
    </div>

    <div v-if="loading" class="text-center py-10">Φόρτωση...</div>
    <div v-else-if="datasets.length === 0" class="text-center py-10 text-gray-500">
      Δεν υπάρχουν datasets ακόμα.
    </div>

    <div v-else class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr>
            <th>Όνομα</th>
            <th>Ημερομηνία</th>
            <th>Status</th>
            <th>Ενέργειες</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in datasets" :key="d.id">
            <td>
              <div v-if="!d.isEditing">
                {{ d.name }}
                <button class="btn btn-ghost btn-xs" @click="startEdit(d)">✏️</button>
              </div>
              <div v-else class="flex gap-2">
                <input v-model="editName" class="input input-bordered input-sm" />
                <button class="btn btn-success btn-sm" @click="saveEdit(d)">Αποθήκευση</button>
                <button class="btn btn-ghost btn-sm" @click="d.isEditing = false">Άκυρο</button>
              </div>
            </td>
            <td>{{ new Date(d.created_at).toLocaleString('el-GR') }}</td>
            <td>
              <span :class="{
                'badge badge-success': d.status === 'uploaded' || d.status === 'ready',
                'badge badge-warning': d.status === 'processing',
                'badge badge-error': d.status === 'failed'
              }">
                {{ d.status || 'uploaded' }}
              </span>
            </td>
            <td class="flex gap-2">
              <button class="btn btn-sm btn-info" @click="openPreview(d)">Προβολή</button>
              <button class="btn btn-sm btn-error" @click="deleteDataset(d.id)">Διαγραφή</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Preview Modal -->
    <dialog id="preview_modal" class="modal">
      <div class="modal-box w-11/12 max-w-5xl">
        <h3 class="font-bold text-lg">Προβολή: {{ selectedDataset?.name }}</h3>
        <div v-if="previewLoading" class="py-10 text-center">Φόρτωση δεδομένων...</div>
        <div v-else-if="previewData.length === 0" class="py-10 text-center text-gray-500">
          Δεν φορτώθηκαν δεδομένα
        </div>
        <div v-else class="overflow-auto max-h-96">
          <table class="table table-xs table-zebra">
            <thead>
              <tr>
                <th v-for="h in Object.keys(previewData[0] || {})" :key="h">{{ h }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in previewData" :key="i">
                <td v-for="(val, key) in row" :key="key">{{ val }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="modal-action">
          <button class="btn" @click="() => { selectedDataset = null; previewData = [] }">Κλείσιμο</button>
        </div>
      </div>
    </dialog>
  </div>
</template>