<script setup lang="ts">
// FILE: src/views/MarketingAI.vue
import { ref } from 'vue'

const platform = ref('instagram')
const tone     = ref('professional')
const product  = ref('')
const audience = ref('')
const result   = ref('')
const loading  = ref(false)
const copied   = ref(false)

const platforms = [
  { value: 'instagram', label: 'Instagram' },
  { value: 'facebook',  label: 'Facebook' },
  { value: 'linkedin',  label: 'LinkedIn' },
  { value: 'twitter',   label: 'X / Twitter' },
]
const tones = [
  { value: 'professional', label: 'Επαγγελματικός' },
  { value: 'friendly',     label: 'Φιλικός' },
  { value: 'bold',         label: 'Δυναμικός' },
  { value: 'minimal',      label: 'Minimal' },
]

const generate = async () => {
  if (!product.value.trim()) return
  loading.value = true; result.value = ''

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 500,
        messages: [{
          role: 'user',
          content: `Δημιούργησε ένα marketing post για ${platform.value} με τόνο: ${tone.value}.
Προϊόν/Υπηρεσία: ${product.value}${audience.value ? `\nΚοινό-στόχος: ${audience.value}` : ''}.
Γράψε ΜΟΝΟ το post (χωρίς εξηγήσεις). Συμπέριλαβε κατάλληλα emojis και hashtags.`
        }]
      })
    })
    const data = await response.json()
    result.value = data.content?.[0]?.text ?? 'Δεν ήρθε απάντηση'
  } catch {
    // Fallback demo
    result.value = `🚀 Γνωρίστε το ${product.value}!\n\nΕίναι καιρός να αναβαθμίσετε την επιχείρησή σας με τη δύναμη της τεχνολογίας. Μην χάσετε την ευκαιρία!\n\n✅ Εύκολο\n✅ Αποτελεσματικό\n✅ Για κάθε επιχείρηση\n\n#Business #AI #Growth #${product.value.replace(/\s+/g,'')}`
  } finally { loading.value = false }
}

const copy = async () => {
  await navigator.clipboard.writeText(result.value)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div class="page-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
      </div>
      <div><h1 class="page-title">Marketing AI</h1><p class="page-sub">Δημιουργία περιεχομένου με AI</p></div>
    </div>

    <div class="cfg-grid">
      <!-- Left: config -->
      <div class="card">
        <div class="card-head"><h3 class="ctitle">Παράμετροι</h3></div>

        <div class="field">
          <label>Προϊόν / Υπηρεσία *</label>
          <input v-model="product" placeholder="π.χ. Νέο AI Εργαλείο" @keydown.enter="generate"/>
        </div>

        <div class="field">
          <label>Κοινό-στόχος</label>
          <input v-model="audience" placeholder="π.χ. μικρές επιχειρήσεις, 25-45 ετών"/>
        </div>

        <div class="field">
          <label>Πλατφόρμα</label>
          <div class="plat-grid">
            <button v-for="p in platforms" :key="p.value"
              class="plat-btn" :class="{active: platform===p.value}"
              @click="platform = p.value">{{ p.label }}</button>
          </div>
        </div>

        <div class="field">
          <label>Τόνος</label>
          <div class="tone-grid">
            <button v-for="t in tones" :key="t.value"
              class="tone-btn" :class="{active: tone===t.value}"
              @click="tone = t.value">{{ t.label }}</button>
          </div>
        </div>

        <button class="btn-gen" :disabled="loading || !product.trim()" @click="generate">
          <span v-if="loading" class="spinner"/>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          {{ loading ? 'Δημιουργία…' : 'Δημιουργία Post' }}
        </button>
      </div>

      <!-- Right: result -->
      <div class="card result-card">
        <div class="card-head">
          <h3 class="ctitle">Αποτέλεσμα</h3>
          <button v-if="result" class="copy-btn" @click="copy">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
            {{ copied ? 'Αντιγράφηκε!' : 'Αντιγραφή' }}
          </button>
        </div>

        <div v-if="loading" class="result-loading">
          <div class="dots"><span/><span/><span/></div>
          <p>Δημιουργία περιεχομένου…</p>
        </div>
        <div v-else-if="result" class="result-text">{{ result }}</div>
        <div v-else class="result-empty">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          <p>Συμπλήρωσε τα πεδία και πάτα "Δημιουργία"</p>
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
.cfg-grid{display:grid;grid-template-columns:1fr 1fr;gap:1.25rem;align-items:start;}
@media(max-width:700px){.cfg-grid{grid-template-columns:1fr;}}
.card{background:#0a1220;border:1px solid #111e33;border-radius:14px;padding:1.5rem;display:flex;flex-direction:column;gap:1.1rem;}
.card-head{display:flex;align-items:center;justify-content:space-between;}
.ctitle{font-size:.9rem;font-weight:700;color:#b8d0ec;margin:0;}
.field{display:flex;flex-direction:column;gap:.4rem;}
label{font-size:.68rem;font-weight:600;color:#2a4060;letter-spacing:.06em;text-transform:uppercase;font-family:'DM Mono',monospace;}
input{background:#080d16;border:1px solid #111e33;border-radius:9px;color:#c8d6e8;padding:.6rem .85rem;font-size:.83rem;font-family:'Sora',sans-serif;outline:none;transition:border-color .15s;}
input:focus{border-color:#2a5299;box-shadow:0 0 0 3px #2a529920;}
input::placeholder{color:#1e3a5a;}
.plat-grid,.tone-grid{display:flex;flex-wrap:wrap;gap:.35rem;}
.plat-btn,.tone-btn{background:#0e1f38;border:1px solid #162a48;color:#3a6080;border-radius:7px;padding:.3rem .7rem;font-size:.75rem;font-family:'Sora',sans-serif;cursor:pointer;transition:all .15s;}
.plat-btn.active,.tone-btn.active{background:#1a3460;border-color:#2a4a7a;color:#7ab8ff;}
.plat-btn:hover:not(.active),.tone-btn:hover:not(.active){border-color:#2a4060;color:#5a8acc;}
.btn-gen{display:flex;align-items:center;justify-content:center;gap:.5rem;background:linear-gradient(135deg,#1a3a6a,#1a2a58);border:1px solid #2a4a8a;color:#7ab8ff;border-radius:10px;padding:.7rem;font-size:.88rem;font-weight:600;font-family:'Sora',sans-serif;cursor:pointer;transition:background .15s,box-shadow .15s;box-shadow:0 4px 20px rgba(74,158,255,.15);}
.btn-gen:hover:not(:disabled){background:linear-gradient(135deg,#22448a,#1a3468);box-shadow:0 4px 24px rgba(74,158,255,.3);}
.btn-gen:disabled{opacity:.35;cursor:not-allowed;}
.copy-btn{display:flex;align-items:center;gap:.4rem;background:#0e1f38;border:1px solid #162a48;color:#4a7acc;border-radius:8px;padding:.3rem .7rem;font-size:.72rem;font-family:'Sora',sans-serif;cursor:pointer;transition:all .15s;}
.copy-btn:hover{background:#1a3460;color:#7ab8ff;}
.result-card{min-height:280px;}
.result-loading,.result-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;flex:1;gap:.75rem;color:#1e3050;font-size:.85rem;padding:2rem;}
.dots{display:flex;gap:.4rem;}.dots span{width:6px;height:6px;background:#2a4a7a;border-radius:50%;animation:pulse 1.2s ease-in-out infinite;}
.dots span:nth-child(2){animation-delay:.2s;}.dots span:nth-child(3){animation-delay:.4s;}
@keyframes pulse{0%,80%,100%{opacity:.2;transform:scale(.8)}40%{opacity:1;transform:scale(1)}}
.result-text{white-space:pre-wrap;font-size:.85rem;color:#b8d0ec;line-height:1.7;background:#080d16;border:1px solid #0e1e33;border-radius:10px;padding:1.1rem;font-family:'DM Mono',monospace;}
.spinner{width:13px;height:13px;border-radius:50%;border:2px solid transparent;border-top-color:currentColor;animation:spin .6s linear infinite;display:inline-block;}
@keyframes spin{to{transform:rotate(360deg)}}
</style>