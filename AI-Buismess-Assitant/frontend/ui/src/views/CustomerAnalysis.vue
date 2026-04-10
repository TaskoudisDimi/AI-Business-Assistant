<!-- ════════════════════════════════════════════════
     FILE: src/views/CustomerAnalysis.vue
════════════════════════════════════════════════ -->
<script setup lang="ts">
import { ref } from 'vue'

// Placeholder data — σύνδεσε με πραγματικό API όταν είναι έτοιμο
const stats = ref({
  total:  312,
  active: 240,
  churn:  8.4,
  ltv:    420
})

const segments = ref([
  { name: 'High Value',    count: 42,  color: '#4a9eff', pct: 13 },
  { name: 'Loyal',         count: 128, color: '#3a9a60', pct: 41 },
  { name: 'At Risk',       count: 36,  color: '#f59e0b', pct: 12 },
  { name: 'New Customers', count: 106, color: '#a78bfa', pct: 34 },
])
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div class="page-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
      </div>
      <div><h1 class="page-title">Customer Analysis</h1><p class="page-sub">Ανάλυση πελατολογίου & τμηματοποίηση</p></div>
    </div>

    <!-- KPIs -->
    <div class="kpi-grid">
      <div class="kpi" style="--c:#4a9eff"><div class="kpi-icon" style="color:#4a9eff;border-color:#4a9eff33;background:#4a9eff10"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg></div><p class="kpi-l">Σύνολο πελατών</p><p class="kpi-v" style="color:#4a9eff">{{ stats.total }}</p></div>
      <div class="kpi" style="--c:#3a9a60"><div class="kpi-icon" style="color:#3a9a60;border-color:#3a9a6033;background:#3a9a6010"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg></div><p class="kpi-l">Ενεργοί</p><p class="kpi-v" style="color:#3a9a60">{{ stats.active }}</p></div>
      <div class="kpi" style="--c:#f59e0b"><div class="kpi-icon" style="color:#f59e0b;border-color:#f59e0b33;background:#f59e0b10"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/></svg></div><p class="kpi-l">Churn Rate</p><p class="kpi-v" style="color:#f59e0b">{{ stats.churn }}%</p></div>
      <div class="kpi" style="--c:#a78bfa"><div class="kpi-icon" style="color:#a78bfa;border-color:#a78bfa33;background:#a78bfa10"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg></div><p class="kpi-l">Avg LTV</p><p class="kpi-v" style="color:#a78bfa">${{ stats.ltv }}</p></div>
    </div>

    <!-- Segments -->
    <div class="card">
      <div class="card-head"><h3 class="ctitle">Τμηματοποίηση πελατών</h3><p class="csub">Κατανομή ανά κατηγορία</p></div>
      <div class="seg-list">
        <div v-for="(s, i) in segments" :key="s.name" class="seg-item" :style="{animationDelay:`${i*60}ms`}">
          <div class="seg-dot" :style="{background:s.color,boxShadow:`0 0 8px ${s.color}88`}" />
          <span class="seg-name">{{ s.name }}</span>
          <div class="seg-bar-wrap">
            <div class="seg-bar" :style="{width:`${s.pct}%`,background:`linear-gradient(90deg, ${s.color}66, ${s.color})`}"/>
          </div>
          <span class="seg-count" :style="{color:s.color}">{{ s.count }}</span>
        </div>
      </div>
    </div>

    <!-- AI Insight -->
    <div class="card insight-card">
      <div class="insight-icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      </div>
      <div><p class="insight-title">AI Insight</p><p class="insight-body">{{ stats.churn > 8 ? `${segments.find(s=>s.name==='At Risk')?.count} πελάτες δείχνουν υψηλή πιθανότητα churn. Εξέτασε στοχευμένη καμπάνια retention.` : 'Το churn rate είναι υγιές. Συνέχισε να εστιάζεις στους Loyal πελάτες.' }}</p></div>
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
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;}
.kpi{background:#0a1220;border:1px solid #111e33;border-radius:14px;padding:1.25rem;display:flex;flex-direction:column;gap:.8rem;transition:border-color .2s;}
.kpi:hover{border-color:var(--c,#4a9eff)33;}
.kpi-icon{width:32px;height:32px;border-radius:9px;border-width:1px;border-style:solid;display:flex;align-items:center;justify-content:center;}
.kpi-l{font-size:.7rem;color:#2a4060;margin:0;font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:.04em;}
.kpi-v{font-size:1.6rem;font-weight:700;margin:0;font-family:'DM Mono',monospace;letter-spacing:-.02em;}
.card{background:#0a1220;border:1px solid #111e33;border-radius:14px;padding:1.5rem;display:flex;flex-direction:column;gap:1rem;}
.card-head{display:flex;flex-direction:column;gap:.2rem;}
.ctitle{font-size:.9rem;font-weight:700;color:#b8d0ec;margin:0;}
.csub{font-size:.75rem;color:#2a4060;margin:0;}
.seg-list{display:flex;flex-direction:column;gap:.65rem;}
.seg-item{display:flex;align-items:center;gap:.85rem;animation:rowIn .3s ease both;}
@keyframes rowIn{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:translateX(0)}}
.seg-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;}
.seg-name{font-size:.82rem;color:#8ab4d8;min-width:120px;}
.seg-bar-wrap{flex:1;height:6px;background:#111e33;border-radius:99px;overflow:hidden;}
.seg-bar{height:100%;border-radius:99px;transition:width .8s cubic-bezier(.4,0,.2,1);}
.seg-count{font-size:.8rem;font-weight:600;font-family:'DM Mono',monospace;min-width:28px;text-align:right;}
.insight-card{flex-direction:row!important;align-items:flex-start;gap:.85rem;background:#0a1a10;border-color:#1a3020;}
.insight-icon{width:30px;height:30px;background:#0d2a1a;border:1px solid #1a4a30;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#3a9a60;flex-shrink:0;}
.insight-title{font-size:.8rem;font-weight:700;color:#3a9a60;margin:0 0 .25rem;}
.insight-body{font-size:.82rem;color:#4a7a58;margin:0;line-height:1.6;}
</style>