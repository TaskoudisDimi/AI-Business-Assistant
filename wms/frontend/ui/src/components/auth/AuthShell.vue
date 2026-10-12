<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import BrandMark from '@/components/BrandMark.vue'
import PrefsToggles from '@/components/PrefsToggles.vue'

defineProps<{ title: string; subtitle?: string }>()

const { t } = useI18n()

// Illustrative rows for the side panel — mirrors the real Inventory screen
const sampleStock = [
  { sku: 'CB-4030', name: 'Carton box 40×30×30', qty: 1240, max: 1500 },
  { sku: 'PW-023',  name: 'Pallet wrap 23μm',     qty: 86,   max: 400, low: true },
  { sku: 'LB-A6',   name: 'Thermal labels A6',    qty: 5300, max: 8000 },
  { sku: 'TP-48',   name: 'Packing tape 48mm',    qty: 31,   max: 300, low: true },
]
</script>

<template>
  <div class="shell">
    <section class="form-col">
      <header class="top">
        <router-link to="/login" :aria-label="t('auth.signIn')"><BrandMark /></router-link>
        <PrefsToggles />
      </header>

      <main class="form-wrap">
        <h1 class="title">{{ title }}</h1>
        <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
        <slot />
      </main>

      <footer class="foot">
        <slot name="footer" />
      </footer>
    </section>

    <aside class="showcase" aria-hidden="true">
      <div class="showcase-inner">
        <p class="eyebrow">{{ t('auth.showcase.eyebrow') }}</p>
        <h2 class="showcase-title">{{ t('auth.showcase.title') }}</h2>

        <div class="preview">
          <div class="preview-head">
            <span>{{ t('nav.inventory') }}</span>
            <span class="preview-badge">2 {{ t('auth.showcase.low') }}</span>
          </div>
          <div v-for="row in sampleStock" :key="row.sku" class="preview-row">
            <span class="sku mono">{{ row.sku }}</span>
            <span class="name">{{ row.name }}</span>
            <span class="bar"><span :class="{ low: row.low }" :style="{ width: `${(row.qty / row.max) * 100}%` }" /></span>
            <span class="qty tabular" :class="{ low: row.low }">{{ row.qty.toLocaleString() }}</span>
          </div>
        </div>

        <ul class="points">
          <li>{{ t('auth.showcase.point1') }}</li>
          <li>{{ t('auth.showcase.point2') }}</li>
          <li>{{ t('auth.showcase.point3') }}</li>
        </ul>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  height: 100%;
  overflow-y: auto;
  background: var(--bg-card);
}
@media (min-width: 960px) {
  .shell { grid-template-columns: minmax(440px, 1fr) minmax(0, 1.1fr); }
}

.form-col {
  display: flex; flex-direction: column;
  min-height: 100%;
  padding: 1.25rem 1.5rem;
}
.top { display: flex; align-items: center; justify-content: space-between; }

.form-wrap {
  width: 100%; max-width: 360px;
  margin: auto;
  padding: 3rem 0;
}
.title { font-size: 1.6rem; font-weight: 650; letter-spacing: -.025em; line-height: 1.2; }
.subtitle { margin-top: .4rem; color: var(--text-sub); font-size: .92rem; }
.form-wrap :slotted(form) { margin-top: 1.75rem; }

.foot { text-align: center; font-size: .86rem; color: var(--text-sub); min-height: 1.5rem; }
.foot :slotted(a) { color: var(--text); font-weight: 550; }
.foot :slotted(a:hover) { color: var(--accent); }

/* ── Showcase panel ── */
.showcase { display: none; }
@media (min-width: 960px) {
  .showcase {
    display: flex; align-items: center; justify-content: center;
    margin: .75rem; border-radius: var(--r-xl);
    background: var(--bg-sunken);
    border: 1px solid var(--border-light);
    padding: 3rem;
  }
}
.showcase-inner { width: 100%; max-width: 460px; }
.eyebrow { font-size: .82rem; font-weight: 550; color: var(--accent); }
.showcase-title {
  margin-top: .5rem;
  font-size: 1.85rem; font-weight: 650; line-height: 1.15; letter-spacing: -.03em;
  text-wrap: balance;
}

.preview {
  margin-top: 2rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}
.preview-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: .75rem 1rem;
  font-size: .85rem; font-weight: 600;
  border-bottom: 1px solid var(--border);
}
.preview-badge {
  font-size: .75rem; font-weight: 550; color: var(--red);
  background: var(--red-bg); padding: .1rem .5rem; border-radius: 999px;
}
.preview-row {
  display: grid; grid-template-columns: 64px 1fr 72px 48px; gap: .75rem; align-items: center;
  padding: .7rem 1rem;
  font-size: .84rem;
}
.preview-row + .preview-row { border-top: 1px solid var(--border-light); }
.sku { font-size: .76rem; color: var(--text-muted); }
.name { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bar { height: 4px; border-radius: 99px; background: var(--bg-hover); overflow: hidden; }
.bar span { display: block; height: 100%; background: var(--text-muted); border-radius: inherit; }
.bar span.low { background: var(--red); }
.qty { text-align: right; font-weight: 550; }
.qty.low { color: var(--red); }

.points { margin-top: 2rem; list-style: none; display: grid; gap: .6rem; }
.points li {
  position: relative; padding-left: 1.4rem;
  font-size: .92rem; color: var(--text-sub);
}
.points li::before {
  content: ''; position: absolute; left: 0; top: .5em;
  width: 8px; height: 8px; border-radius: 2px; background: var(--accent);
}
</style>
