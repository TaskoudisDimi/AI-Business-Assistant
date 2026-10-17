<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore, apiErrorMessage } from '@/stores/auth'
import { api } from '@/services/api'

interface Member { user_id: string; role: 'owner' | 'admin' | 'member'; email: string | null; full_name: string | null; pending: boolean; is_you: boolean }

const { t } = useI18n()
const auth = useAuthStore()
const bid = computed(() => auth.currentBusiness?.id ?? '')
const members = ref<Member[]>([])
const email = ref('')
const role = ref<'member' | 'admin'>('member')
const busy = ref(false)
const msg = ref<{ type: 'error' | 'success'; text: string } | null>(null)

async function load() {
  members.value = (await api.get(`/businesses/${bid.value}/members`)).data
}
onMounted(load)

async function invite() {
  busy.value = true; msg.value = null
  try {
    const { data } = await api.post(`/businesses/${bid.value}/members`, { email: email.value.trim(), role: role.value })
    msg.value = { type: 'success', text: data.invited ? t('team.invited', { email: email.value }) : t('team.added', { email: email.value }) }
    email.value = ''
    await load()
  } catch (e) {
    const m = apiErrorMessage(e)
    msg.value = { type: 'error', text: m === 'Already a member' ? t('team.already') : m || t('common.error') }
  } finally { busy.value = false }
}

async function setRole(m: Member, r: 'member' | 'admin') {
  await api.patch(`/businesses/${bid.value}/members/${m.user_id}`, { role: r })
  m.role = r
}

async function remove(m: Member) {
  if (!confirm(m.is_you ? t('team.confirmLeave') : t('team.confirmRemove', { name: m.full_name || m.email }))) return
  await api.delete(`/businesses/${bid.value}/members/${m.user_id}`)
  if (m.is_you) window.location.href = '/dashboard'
  else await load()
}
</script>

<template>
  <div class="ui-card">
    <div class="ui-card-head">
      <div>
        <p class="ui-card-title">{{ t('team.title') }}</p>
        <p class="ui-card-sub">{{ t('team.sub') }}</p>
      </div>
    </div>
    <div class="ui-table-wrap">
      <table class="ui-table">
        <tbody>
          <tr v-for="m in members" :key="m.user_id">
            <td>
              <div class="who">{{ m.full_name || m.email }} <span v-if="m.is_you" class="ui-muted">({{ t('team.you') }})</span></div>
              <div class="ui-muted small">{{ m.email }} <span v-if="m.pending" class="ui-badge">{{ t('team.pending') }}</span></div>
            </td>
            <td class="num">
              <span v-if="m.role === 'owner' || !auth.isAdmin" class="ui-badge" :class="{ 'ui-badge--accent': m.role === 'owner' }">{{ t(`team.roles.${m.role}`) }}</span>
              <select v-else :value="m.role" class="ui-select ui-input--sm role" @change="setRole(m, ($event.target as HTMLSelectElement).value as 'member' | 'admin')">
                <option value="member">{{ t('team.roles.member') }}</option>
                <option value="admin">{{ t('team.roles.admin') }}</option>
              </select>
            </td>
            <td class="num">
              <button v-if="m.role !== 'owner' && (auth.isAdmin || m.is_you)" class="ui-btn ui-btn--ghost ui-btn--sm" @click="remove(m)">
                {{ m.is_you ? t('team.leave') : t('team.remove') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <form v-if="auth.isAdmin" class="ui-card-body invite" @submit.prevent="invite">
      <input v-model="email" class="ui-input" type="email" required :placeholder="t('team.emailPlaceholder')" />
      <select v-model="role" class="ui-select role">
        <option value="member">{{ t('team.roles.member') }}</option>
        <option value="admin">{{ t('team.roles.admin') }}</option>
      </select>
      <button class="ui-btn ui-btn--primary" :disabled="busy || !email">{{ t('team.invite') }}</button>
    </form>
    <div class="ui-card-body">
      <p v-if="msg" class="ui-alert" :class="msg.type === 'error' ? 'ui-alert--error' : 'ui-alert--success'">{{ msg.text }}</p>
      <p class="ui-hint">{{ t('team.rolesHelp') }}</p>
    </div>
  </div>
</template>

<style scoped>
.who { font-weight: 550; }
.small { font-size: .8rem; margin-top: .1rem; }
.role { width: 140px; margin-left: auto; }
.invite { display: flex; gap: .5rem; border-top: 1px solid var(--border-light); flex-wrap: wrap; }
.invite .ui-input { flex: 1; min-width: 200px; }
</style>
