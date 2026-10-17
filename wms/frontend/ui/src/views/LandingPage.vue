<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import BrandMark from '@/components/BrandMark.vue'
import PrefsToggles from '@/components/PrefsToggles.vue'
import AppPreview from '@/components/landing/AppPreview.vue'

const { t, tm } = useI18n()

// The page scrolls inside .landing (html/body are overflow:hidden for the app shell),
// so anchor links scroll that container instead of relying on the URL hash.
const scroller = ref<HTMLElement | null>(null)
const goTo = (id: string) => {
  scroller.value?.querySelector(`#${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const navLinks = ['features', 'how', 'who', 'faq'] as const
const features = ['inventory', 'reorder', 'forecast', 'customers'] as const
const extras   = ['orders', 'datasets', 'language', 'access'] as const
const steps    = ['products', 'orders', 'insights'] as const
const audience = ['retail', 'wholesale', 'eshop', 'food'] as const
const faqCount = (tm('landing.faq.items') as unknown[]).length
</script>

<template>
  <div ref="scroller" class="landing">
    <!-- ── Header ── -->
    <header class="header">
      <div class="wrap header-inner">
        <router-link to="/" class="logo" aria-label="WMS"><BrandMark :size="26" /></router-link>
        <nav class="links">
          <button v-for="l in navLinks" :key="l" @click="goTo(l)">{{ t(`landing.nav.${l}`) }}</button>
        </nav>
        <div class="header-actions">
          <PrefsToggles />
          <router-link to="/login" class="ui-btn ui-btn--ghost sm">{{ t('auth.signIn') }}</router-link>
          <router-link to="/register" class="ui-btn ui-btn--primary sm hide-sm">{{ t('landing.cta.start') }}</router-link>
        </div>
      </div>
    </header>

    <main>
      <!-- ── Hero ── -->
      <section class="hero wrap">
        <div class="hero-copy">
          <p class="eyebrow">{{ t('landing.hero.eyebrow') }}</p>
          <h1>{{ t('landing.hero.title') }}</h1>
          <p class="lead">{{ t('landing.hero.lead') }}</p>
          <div class="cta-row">
            <router-link to="/register" class="ui-btn ui-btn--primary lg">{{ t('landing.cta.start') }}</router-link>
            <button class="ui-btn ui-btn--ghost lg" @click="goTo('features')">{{ t('landing.cta.tour') }}</button>
          </div>
          <p class="fine">{{ t('landing.hero.fine') }}</p>
        </div>
        <div class="hero-visual">
          <AppPreview />
        </div>
      </section>

      <!-- ── Features ── -->
      <section id="features" class="section wrap">
        <div class="section-head">
          <p class="eyebrow">{{ t('landing.nav.features') }}</p>
          <h2>{{ t('landing.features.title') }}</h2>
          <p class="sub">{{ t('landing.features.sub') }}</p>
        </div>

        <div class="feature-grid">
          <article v-for="f in features" :key="f" class="feature">
            <div class="feature-visual" :class="`fv-${f}`" aria-hidden="true">
              <!-- inventory: stock moving in and out -->
              <template v-if="f === 'inventory'">
                <div class="mv"><span class="mv-in">+120</span><span>{{ t('landing.visual.inbound') }}</span><b>CB-4030</b></div>
                <div class="mv"><span class="mv-out">−36</span><span>{{ t('landing.visual.outbound') }}</span><b>LB-A6</b></div>
                <div class="mv"><span class="mv-out">−8</span><span>{{ t('landing.visual.outbound') }}</span><b>PW-023</b></div>
              </template>
              <!-- reorder: days to stockout -->
              <template v-else-if="f === 'reorder'">
                <div v-for="(d, i) in [2, 4, 11]" :key="i" class="stock">
                  <span class="stock-bar"><span :style="{ width: `${d * 7}%` }" :class="{ crit: d < 7 }" /></span>
                  <span class="stock-d" :class="{ crit: d < 7 }">{{ t('wms.inventory.ai.daysLeft', { days: d }) }}</span>
                </div>
              </template>
              <!-- forecast: bars + dashed projection -->
              <template v-else-if="f === 'forecast'">
                <div class="bars">
                  <span v-for="(h, i) in [40, 55, 48, 62, 58, 70]" :key="i" :style="{ height: `${h}%` }" />
                  <span v-for="(h, i) in [74, 69, 80]" :key="`f${i}`" class="proj" :style="{ height: `${h}%` }" />
                </div>
              </template>
              <!-- customers: segments -->
              <template v-else>
                <div class="segs">
                  <span v-for="s in ['high_value', 'loyal', 'new', 'at_risk']" :key="s" class="seg" :class="`seg--${s}`">
                    {{ t(`customers.segments.${s}`) }}
                  </span>
                </div>
              </template>
            </div>
            <h3>{{ t(`landing.features.${f}.title`) }}</h3>
            <p>{{ t(`landing.features.${f}.body`) }}</p>
          </article>
        </div>

        <ul class="extras">
          <li v-for="e in extras" :key="e">
            <strong>{{ t(`landing.extras.${e}.title`) }}</strong>
            <span>{{ t(`landing.extras.${e}.body`) }}</span>
          </li>
        </ul>
      </section>

      <!-- ── How it works ── -->
      <section id="how" class="section section--tint">
        <div class="wrap">
          <div class="section-head">
            <p class="eyebrow">{{ t('landing.nav.how') }}</p>
            <h2>{{ t('landing.how.title') }}</h2>
          </div>
          <ol class="steps">
            <li v-for="(s, i) in steps" :key="s" class="step">
              <span class="step-n">{{ i + 1 }}</span>
              <h3>{{ t(`landing.how.${s}.title`) }}</h3>
              <p>{{ t(`landing.how.${s}.body`) }}</p>
            </li>
          </ol>
        </div>
      </section>

      <!-- ── Who it's for ── -->
      <section id="who" class="section wrap">
        <div class="section-head">
          <p class="eyebrow">{{ t('landing.nav.who') }}</p>
          <h2>{{ t('landing.who.title') }}</h2>
        </div>
        <div class="audience">
          <div v-for="a in audience" :key="a" class="aud">
            <h3>{{ t(`landing.who.${a}.title`) }}</h3>
            <p>{{ t(`landing.who.${a}.body`) }}</p>
          </div>
        </div>
      </section>

      <!-- ── FAQ ── -->
      <section id="faq" class="section wrap faq-wrap">
        <div class="section-head">
          <p class="eyebrow">{{ t('landing.nav.faq') }}</p>
          <h2>{{ t('landing.faq.title') }}</h2>
        </div>
        <div class="faq">
          <details v-for="i in faqCount" :key="i">
            <summary>{{ t(`landing.faq.items.${i - 1}.q`) }}</summary>
            <p>{{ t(`landing.faq.items.${i - 1}.a`) }}</p>
          </details>
        </div>
      </section>

      <!-- ── Closing CTA ── -->
      <section class="wrap">
        <div class="closing">
          <h2>{{ t('landing.closing.title') }}</h2>
          <p>{{ t('landing.closing.body') }}</p>
          <div class="cta-row">
            <router-link to="/register" class="ui-btn ui-btn--primary lg">{{ t('landing.cta.start') }}</router-link>
            <router-link to="/login" class="ui-btn ui-btn--ghost lg">{{ t('auth.signIn') }}</router-link>
          </div>
        </div>
      </section>
    </main>

    <footer class="footer wrap">
      <BrandMark :size="20" />
      <span class="muted">© {{ new Date().getFullYear() }} TaskCode</span>
      <nav>
        <router-link to="/privacy">{{ t('legal.privacyTitle') }}</router-link>
        <router-link to="/terms">{{ t('legal.termsTitle') }}</router-link>
        <router-link to="/login">{{ t('auth.signIn') }}</router-link>
      </nav>
    </footer>
  </div>
</template>

<style scoped>
.landing { height: 100%; overflow-y: auto; background: var(--bg-card); scroll-padding-top: 72px; }
.wrap { width: 100%; max-width: 1160px; margin: 0 auto; padding: 0 24px; }

/* ── Header ── */
.header {
  position: sticky; top: 0; z-index: 10;
  background: color-mix(in srgb, var(--bg-card) 86%, transparent);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-light);
}
.header-inner { display: flex; align-items: center; gap: 24px; height: 64px; }
.logo { display: flex; }
.links { display: flex; gap: 4px; margin-right: auto; }
.links button {
  background: none; padding: 6px 10px; border-radius: var(--r);
  color: var(--text-sub); font-size: .9rem; cursor: pointer;
}
.links button:hover { color: var(--text); background: var(--bg-hover); }
.header-actions { display: flex; align-items: center; gap: 8px; }
.ui-btn.sm { height: 34px; padding: 0 .85rem; font-size: .875rem; }
.ui-btn.lg { height: 44px; padding: 0 1.25rem; font-size: .95rem; }
@media (max-width: 860px) { .links { display: none; } .header-actions { margin-left: auto; } }
@media (max-width: 480px) { .hide-sm { display: none; } }

/* ── Type ── */
.eyebrow { font-size: .85rem; font-weight: 600; color: var(--accent); }
h1 {
  margin-top: 14px;
  font-size: clamp(2rem, 3.6vw, 3.05rem); line-height: 1.08; letter-spacing: -.035em; font-weight: 680;
  text-wrap: balance;
}
h2 { margin-top: 10px; font-size: clamp(1.6rem, 3vw, 2.3rem); line-height: 1.12; letter-spacing: -.03em; font-weight: 650; text-wrap: balance; }
h3 { font-size: 1.05rem; font-weight: 620; letter-spacing: -.01em; }
.lead { margin-top: 18px; font-size: 1.12rem; line-height: 1.55; color: var(--text-sub); max-width: 34rem; }
.sub { margin-top: 12px; font-size: 1.02rem; color: var(--text-sub); max-width: 40rem; }
.muted { color: var(--text-muted); }

/* ── Hero ── */
.hero {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 56px; align-items: center;
  padding-top: 72px; padding-bottom: 88px;
}
.cta-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 28px; }
.fine { margin-top: 14px; font-size: .85rem; color: var(--text-muted); }
@media (max-width: 960px) {
  .hero { grid-template-columns: 1fr; gap: 40px; padding-top: 48px; padding-bottom: 56px; }
}

/* ── Sections ── */
.section { padding-top: 88px; padding-bottom: 88px; }
.section--tint { background: var(--bg); border-top: 1px solid var(--border-light); border-bottom: 1px solid var(--border-light); }
.section-head { margin-bottom: 40px; }

.feature-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
@media (max-width: 760px) { .feature-grid { grid-template-columns: 1fr; } }
.feature {
  padding: 22px; border: 1px solid var(--border); border-radius: var(--r-xl); background: var(--bg-card);
  display: flex; flex-direction: column; gap: 8px;
}
.feature p { color: var(--text-sub); line-height: 1.55; }
.feature-visual {
  height: 128px; margin-bottom: 10px; padding: 14px 16px;
  border-radius: var(--r-lg); background: var(--bg-sunken); border: 1px solid var(--border-light);
  display: flex; flex-direction: column; justify-content: center; gap: 8px; font-size: .82rem;
}
.mv { display: grid; grid-template-columns: 44px 1fr auto; gap: 10px; align-items: center; color: var(--text-sub); }
.mv b { font-family: 'Geist Mono Variable', monospace; font-weight: 500; font-size: .76rem; color: var(--text-muted); }
.mv-in, .mv-out { font-weight: 650; font-variant-numeric: tabular-nums; }
.mv-in { color: var(--green); } .mv-out { color: var(--text); }
.stock { display: grid; grid-template-columns: 1fr 64px; gap: 12px; align-items: center; }
.stock-bar { height: 6px; border-radius: 99px; background: var(--border); overflow: hidden; }
.stock-bar span { display: block; height: 100%; background: var(--amber); border-radius: inherit; }
.stock-bar span.crit, .stock-d.crit { background: var(--red); }
.stock-d { font-weight: 600; color: var(--amber); text-align: right; font-size: .78rem; }
.stock-d.crit { background: none; color: var(--red); }
.bars { display: flex; align-items: flex-end; gap: 6px; height: 100%; }
.bars span { flex: 1; background: var(--border-mid); border-radius: 3px 3px 0 0; }
.bars span.proj { background: repeating-linear-gradient(-45deg, var(--accent-soft) 0 4px, var(--accent-line) 4px 8px); outline: 1px dashed var(--accent); outline-offset: -1px; }
.segs { display: flex; flex-wrap: wrap; gap: 8px; }
.seg { padding: 4px 10px; border-radius: 99px; font-weight: 550; font-size: .8rem; border: 1px solid; }
.seg--high_value { color: var(--accent); border-color: var(--accent-line); background: var(--accent-soft); }
.seg--loyal { color: var(--green); border-color: rgba(var(--green-rgb), .3); background: var(--green-bg); }
.seg--new { color: var(--blue); border-color: rgba(var(--blue-rgb), .3); background: rgba(var(--blue-rgb), .08); }
.seg--at_risk { color: var(--amber); border-color: rgba(var(--amber-rgb), .35); background: rgba(var(--amber-rgb), .08); }

.extras {
  list-style: none; margin-top: 16px;
  display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px;
  padding: 22px; border: 1px solid var(--border); border-radius: var(--r-xl);
}
.extras li { display: flex; flex-direction: column; gap: 4px; font-size: .9rem; }
.extras span { color: var(--text-sub); line-height: 1.5; }
@media (max-width: 860px) { .extras { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 480px) { .extras { grid-template-columns: 1fr; } }

.steps { list-style: none; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 32px; }
@media (max-width: 760px) { .steps { grid-template-columns: 1fr; gap: 24px; } }
.step { display: flex; flex-direction: column; gap: 8px; padding-top: 18px; border-top: 2px solid var(--text); }
.step p { color: var(--text-sub); line-height: 1.55; }
.step-n { font-family: 'Geist Mono Variable', monospace; font-size: .85rem; color: var(--text-muted); }

.audience { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
@media (max-width: 960px) { .audience { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 480px) { .audience { grid-template-columns: 1fr; } }
.aud { padding: 20px; border-radius: var(--r-xl); background: var(--bg); border: 1px solid var(--border-light); display: flex; flex-direction: column; gap: 6px; }
.aud p { color: var(--text-sub); line-height: 1.5; font-size: .92rem; }

.faq-wrap { max-width: 820px; }
.faq { border-top: 1px solid var(--border); }
.faq details { border-bottom: 1px solid var(--border); }
.faq summary {
  list-style: none; cursor: pointer;
  display: flex; justify-content: space-between; gap: 16px;
  padding: 18px 0; font-weight: 560; font-size: 1rem;
}
.faq summary::-webkit-details-marker { display: none; }
.faq summary::after { content: '+'; color: var(--text-muted); font-size: 1.2rem; line-height: 1; transition: transform .15s; }
.faq details[open] summary::after { transform: rotate(45deg); }
.faq details p { padding: 0 0 18px; color: var(--text-sub); line-height: 1.6; max-width: 44rem; }

.closing {
  margin: 24px 0 88px; padding: 56px 40px; border-radius: 20px; text-align: center;
  background: var(--brand-dark); color: #fff;
}
.closing h2 { margin: 0 auto; max-width: 36rem; color: #fff; }
.closing p { margin: 12px auto 0; max-width: 32rem; color: rgba(255, 255, 255, .78); font-size: 1.02rem; }
.closing .cta-row { justify-content: center; }
.closing .ui-btn--primary { background: var(--brand-light); color: #06201d; }
.closing .ui-btn--primary:hover { background: #5fcfbf; }
.closing .ui-btn--ghost { color: #fff; border-color: rgba(255, 255, 255, .35); }
.closing .ui-btn--ghost:hover { background: rgba(255, 255, 255, .08); color: #fff; }
@media (max-width: 480px) { .closing { padding: 40px 20px; } }

.footer {
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  padding-top: 28px; padding-bottom: 28px; border-top: 1px solid var(--border-light);
  font-size: .875rem;
}
.footer nav { margin-left: auto; display: flex; gap: 18px; }
.footer nav a { color: var(--text-sub); }
.footer nav a:hover { color: var(--text); }
</style>
