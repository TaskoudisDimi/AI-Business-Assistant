<!-- ════════════ History.vue ════════════ -->
<script setup lang="ts">
// FILE: src/views/History.vue
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'

const history = ref<any[]>([])
const loading = ref(false)
const filter  = ref<'all'|'sales_forecast'>('all')

onMounted(async () => {
  loading.value = true
  try {
    const r = await api.get('/predictions')
    history.value = r.data
  } catch {}
  loading.value = false
})

const filtered = computed(() =>
  filter.value === 'all' ? history.value : history.value.filter(h => h.type === filter.value)
)

const fmt     = (v: number) => v?.toLocaleString('el-GR', { maximumFractionDigits: 2 }) ?? '—'
const fmtDate = (iso: string) => new Date(iso).toLocaleString('el-GR', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' })
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div class="page-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      </div>
      <div><h1 class="page-title">Ιστορικό</h1><p class="page-sub">Όλες οι προβλέψεις και αναλύσεις</p></div>
    </div>

    <div class="filters">
      <button class="fil-btn" :class="{active: filter==='all'}"           @click="filter='all'">Όλα</button>
      <button class="fil-btn" :class="{active: filter==='sales_forecast'}" @click="filter='sales_forecast'">Sales Forecast</button>
    </div>

    <div class="card">
      <div v-if="loading" class="state"><div class="dots"><span/><span/><span/></div><p>Φόρτωση…</p></div>
      <div v-else-if="!filtered.length" class="state">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        <p>Δεν υπάρχουν αποτελέσματα</p>
      </div>
      <div v-else class="hist-list">
        <div v-for="(h, i) in filtered" :key="h.id" class="hist-item" :style="{animationDelay:`${i*40}ms`}">
          <div class="hist-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/></svg>
          </div>
          <div class="hist-info">
            <p class="hist-type">{{ h.type?.replace('_',' ') ?? 'Prediction' }}</p>
            <p class="hist-date">{{ fmtDate(h.created_at) }}</p>
          </div>
          <div class="hist-stats">
            <span v-if="h.result?.summary" class="hist-tag">
              avg {{ fmt(h.result.summary.avg) }} / ημ.
            </span>
            <span v-if="h.result?.summary?.total" class="hist-tag hist-tag--blue">
              {{ fmt(h.result.summary.total) }} total
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@400;500;600;700&display=swap');
.page{min-height:100vh;padding:2rem 2.5rem;background:#080d16;font-family:'Sora',sans-serif;color:#c8d6e8;display:flex;flex-direction:column;gap:1.5rem;}
.page-header{display:flex;align-items:center;gap:1rem;}
.page-icon{width:44px;height:44px;background:linear-gradient(135deg,#1a2640,#0e1a2e);border:1px solid #1e3050;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#4a9eff;}
.page-title{font-size:1.4rem;font-weight:700;color:#e8f0fe;margin:0;letter-spacing:-.02em;}
.page-sub{font-size:.78rem;color:#3d5570;margin:.1rem 0 0;font-family:'DM Mono',monospace;}
.filters{display:flex;gap:.35rem;}
.fil-btn{background:#0a1220;border:1px solid #111e33;color:#3a5a80;border-radius:9px;padding:.45rem .9rem;font-size:.78rem;font-weight:500;font-family:'Sora',sans-serif;cursor:pointer;transition:all .15s;}
.fil-btn.active{background:#0d2040;border-color:#1a3460;color:#7ab8ff;}
.fil-btn:hover:not(.active){background:#0d1f38;color:#7ab0e0;}
.card{background:#0a1220;border:1px solid #111e33;border-radius:14px;padding:1.5rem;}
.state{display:flex;flex-direction:column;align-items:center;padding:3.5rem;gap:.75rem;color:#1e3050;font-size:.85rem;}
.dots{display:flex;gap:.4rem;} .dots span{width:6px;height:6px;background:#2a4a7a;border-radius:50%;animation:pulse 1.2s ease-in-out infinite;}
.dots span:nth-child(2){animation-delay:.2s;} .dots span:nth-child(3){animation-delay:.4s;}
@keyframes pulse{0%,80%,100%{opacity:.2;transform:scale(.8)}40%{opacity:1;transform:scale(1)}}
.hist-list{display:flex;flex-direction:column;gap:.45rem;}
.hist-item{display:flex;align-items:center;gap:.85rem;background:#080d16;border:1px solid #0e1e33;border-radius:10px;padding:.85rem 1rem;transition:background .12s;animation:rowIn .3s ease both;}
@keyframes rowIn{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
.hist-item:hover{background:#0d1f38;}
.hist-icon{width:32px;height:32px;background:#0e1f38;border:1px solid #162a48;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#3a6fcc;flex-shrink:0;}
.hist-info{flex:1;}
.hist-type{font-size:.82rem;font-weight:600;color:#8ab4d8;margin:0;text-transform:capitalize;}
.hist-date{font-size:.68rem;color:#2a4060;margin:.1rem 0 0;font-family:'DM Mono',monospace;}
.hist-stats{display:flex;gap:.4rem;flex-wrap:wrap;}
.hist-tag{background:#0d2040;border:1px solid #1a3460;color:#5a8acc;font-size:.68rem;padding:.18rem .5rem;border-radius:999px;font-family:'DM Mono',monospace;}
.hist-tag--blue{background:#0a1a2a;border-color:#1a3050;color:#4a9eff;}
</style>