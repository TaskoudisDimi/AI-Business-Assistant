<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore, apiErrorMessage } from '@/stores/auth'
import { api } from '@/services/api'
import { renderMarkdown } from '@/utils/markdown'

interface Msg { role: 'user' | 'assistant'; content: string; error?: boolean }

const { t, tm, locale } = useI18n()
const auth = useAuthStore()
const businessId = computed(() => auth.currentBusiness?.id ?? '')
const key = computed(() => `assistant:${businessId.value}`)

const messages = ref<Msg[]>([])
const draft = ref('')
const sending = ref(false)
const status = ref<{ enabled: boolean; remaining_today: number } | null>(null)
const scroller = ref<HTMLElement | null>(null)
const suggestions = computed(() => tm('assistant.suggestions') as string[])

onMounted(async () => {
  try { messages.value = JSON.parse(sessionStorage.getItem(key.value) || '[]') } catch { /* none */ }
  try {
    status.value = (await api.get('/ai/status', { params: { business_id: businessId.value } })).data
  } catch { status.value = { enabled: false, remaining_today: 0 } }
  scrollDown()
})
watch(messages, v => { try { sessionStorage.setItem(key.value, JSON.stringify(v.slice(-30))) } catch { /* ignore */ } }, { deep: true })

async function scrollDown() {
  await nextTick()
  scroller.value?.scrollTo({ top: scroller.value.scrollHeight, behavior: 'smooth' })
}

async function send(text?: string) {
  const content = (text ?? draft.value).trim()
  if (!content || sending.value) return
  draft.value = ''
  messages.value.push({ role: 'user', content })
  sending.value = true
  scrollDown()
  try {
    const history = messages.value.filter(m => !m.error).slice(-20).map(({ role, content }) => ({ role, content }))
    const { data } = await api.post('/ai/chat', { business_id: businessId.value, messages: history, language: locale.value },
      { timeout: 180_000 })
    messages.value.push({ role: 'assistant', content: data.reply })
    if (status.value) status.value.remaining_today = Math.max(0, status.value.remaining_today - 1)
  } catch (e) {
    messages.value.push({ role: 'assistant', content: apiErrorMessage(e) || t('common.error'), error: true })
  } finally {
    sending.value = false
    scrollDown()
  }
}

function reset() { messages.value = [] }
</script>

<template>
  <div class="assistant">
    <div ref="scroller" class="thread">
      <div class="inner">
        <div v-if="status && !status.enabled" class="ui-alert ui-alert--warn">{{ t('assistant.disabled') }}</div>

        <div v-if="!messages.length" class="intro">
          <h2>{{ t('assistant.title') }}</h2>
          <p class="ui-muted">{{ t('assistant.intro') }}</p>
          <div class="chips">
            <button v-for="q in suggestions" :key="q" class="chip" :disabled="!status?.enabled" @click="send(q)">{{ q }}</button>
          </div>
        </div>

        <div v-for="(m, i) in messages" :key="i" class="msg" :class="[m.role, { error: m.error }]">
          <div v-if="m.role === 'user'" class="bubble">{{ m.content }}</div>
          <!-- eslint-disable-next-line vue/no-v-html — renderMarkdown escapes all input -->
          <div v-else class="answer" v-html="renderMarkdown(m.content)" />
        </div>
        <div v-if="sending" class="msg assistant"><div class="answer thinking"><span /><span /><span /></div></div>
      </div>
    </div>

    <form class="composer" @submit.prevent="send()">
      <div class="inner row">
        <textarea v-model="draft" class="ui-textarea" rows="1" :placeholder="t('assistant.placeholder')"
          :disabled="!status?.enabled" @keydown.enter.exact.prevent="send()" />
        <button class="ui-btn ui-btn--primary" :disabled="!draft.trim() || sending || !status?.enabled">{{ t('assistant.send') }}</button>
      </div>
      <div class="inner meta">
        <span>{{ t('assistant.disclaimer') }}</span>
        <button v-if="messages.length" type="button" class="link" @click="reset">{{ t('assistant.newChat') }}</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.assistant { height: 100%; display: flex; flex-direction: column; }
.thread { flex: 1; overflow-y: auto; }
.inner { max-width: 760px; margin: 0 auto; padding: 0 1.25rem; }
.thread .inner { padding-top: 1.5rem; padding-bottom: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
.intro { padding: 8vh 0 1rem; }
.intro h2 { font-size: 1.5rem; font-weight: 650; letter-spacing: -.02em; }
.intro p { margin-top: .4rem; }
.chips { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: 1.25rem; }
.chip { background: var(--bg-card); border: 1px solid var(--border); border-radius: 99px; padding: .45rem .85rem; font-size: .85rem; color: var(--text-sub); cursor: pointer; text-align: left; }
.chip:hover:not(:disabled) { border-color: var(--accent-line); color: var(--text); }
.msg.user { display: flex; justify-content: flex-end; }
.bubble { background: var(--accent-soft); color: var(--text); padding: .6rem .9rem; border-radius: 14px 14px 4px 14px; max-width: 80%; white-space: pre-wrap; }
.answer { line-height: 1.6; font-size: .93rem; }
.msg.error .answer { color: var(--red); }
.answer :deep(p + p), .answer :deep(p + table), .answer :deep(table + p), .answer :deep(ul), .answer :deep(ol) { margin-top: .6rem; }
.answer :deep(ul), .answer :deep(ol) { padding-left: 1.25rem; }
.answer :deep(table) { border-collapse: collapse; font-size: .85rem; margin-top: .4rem; width: 100%; }
.answer :deep(th), .answer :deep(td) { padding: .4rem .6rem; border-bottom: 1px solid var(--border); text-align: left; }
.answer :deep(td.num) { text-align: right; font-variant-numeric: tabular-nums; }
.answer :deep(code) { font-family: 'Geist Mono Variable', monospace; font-size: .85em; background: var(--bg-hover); padding: .05rem .3rem; border-radius: 4px; }
.thinking { display: flex; gap: .3rem; padding: .5rem 0; }
.thinking span { width: 6px; height: 6px; border-radius: 50%; background: var(--text-muted); animation: blink 1.2s infinite; }
.thinking span:nth-child(2) { animation-delay: .2s; }
.thinking span:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%, 80%, 100% { opacity: .25 } 40% { opacity: 1 } }
.composer { border-top: 1px solid var(--border); background: var(--bg); padding: .75rem 0; }
.row { display: flex; gap: .5rem; align-items: flex-end; }
.row .ui-textarea { min-height: 44px; max-height: 160px; flex: 1; }
.meta { display: flex; justify-content: space-between; margin-top: .4rem; font-size: .75rem; color: var(--text-muted); }
.link { background: none; color: var(--text-sub); cursor: pointer; font-size: .75rem; }
</style>
