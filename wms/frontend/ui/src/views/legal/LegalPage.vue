<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import BrandMark from '@/components/BrandMark.vue'
import PrefsToggles from '@/components/PrefsToggles.vue'
import { privacy, terms } from '@/legal/documents'
import { site } from '@/config/site'
import { intlLocale } from '@/i18n/format'

const props = defineProps<{ doc: 'privacy' | 'terms' }>()
const { t, locale } = useI18n()
const content = computed(() => (props.doc === 'privacy' ? privacy : terms)(locale.value === 'en' ? 'en' : 'el'))
</script>

<template>
  <div class="legal">
    <header class="top">
      <router-link to="/" aria-label="WMS"><BrandMark :size="24" /></router-link>
      <PrefsToggles />
    </header>
    <article>
      <h1>{{ content.title }}</h1>
      <p class="updated">{{ t('legal.updated', { date: new Date(site.policyUpdated).toLocaleDateString(intlLocale(), { dateStyle: 'long' }) }) }}</p>
      <p class="intro">{{ content.intro }}</p>
      <section v-for="s in content.sections" :key="s.h">
        <h2>{{ s.h }}</h2>
        <p v-for="(p, i) in s.p" :key="i">{{ p }}</p>
      </section>
      <nav class="other">
        <router-link :to="doc === 'privacy' ? '/terms' : '/privacy'">
          {{ doc === 'privacy' ? t('legal.termsTitle') : t('legal.privacyTitle') }} →
        </router-link>
      </nav>
    </article>
  </div>
</template>

<style scoped>
.legal { height: 100%; overflow-y: auto; background: var(--bg-card); }
.top { display: flex; justify-content: space-between; align-items: center; max-width: 760px; margin: 0 auto; padding: 1.25rem 24px; }
article { max-width: 760px; margin: 0 auto; padding: 1.5rem 24px 5rem; }
h1 { font-size: 2rem; font-weight: 660; letter-spacing: -.03em; }
.updated { margin-top: .4rem; color: var(--text-muted); font-size: .85rem; }
.intro { margin-top: 1.25rem; font-size: 1.05rem; color: var(--text-sub); line-height: 1.6; }
section { margin-top: 2rem; }
h2 { font-size: 1.1rem; font-weight: 620; }
section p { margin-top: .6rem; line-height: 1.65; color: var(--text-sub); }
.other { margin-top: 3rem; padding-top: 1.25rem; border-top: 1px solid var(--border-light); }
.other a { color: var(--accent); font-weight: 550; }
</style>
