<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const { t } = useI18n()
const collapsed = ref(false)

const menuGroups = [
  {
    labelKey: 'sidebar.analytics',
    items: [
      {
        key: 'nav.dashboard',
        path: '/dashboard',
        icon: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <rect x="3" y="3" width="7" height="7" rx="1.5"/>
          <rect x="14" y="3" width="7" height="7" rx="1.5"/>
          <rect x="3" y="14" width="7" height="7" rx="1.5"/>
          <rect x="14" y="14" width="7" height="7" rx="1.5"/>
        </svg>`,
      },
      {
        key: 'nav.salesForecast',
        path: '/sales',
        icon: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
          <polyline points="16 7 22 7 22 13"/>
        </svg>`,
      },
      {
        key: 'nav.customerAnalysis',
        path: '/customers',
        icon: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 00-3-3.87"/>
          <path d="M16 3.13a4 4 0 010 7.75"/>
        </svg>`,
      },
    ],
  },
  {
    labelKey: 'sidebar.warehouse',
    items: [
      {
        key: 'nav.inventory',
        path: '/inventory',
        icon: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <rect x="2" y="7" width="20" height="14" rx="2"/>
          <path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/>
          <line x1="12" y1="12" x2="12" y2="16"/>
          <line x1="10" y1="14" x2="14" y2="14"/>
        </svg>`,
      },
      {
        key: 'nav.products',
        path: '/products',
        icon: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
          <line x1="12" y1="22.08" x2="12" y2="12"/>
        </svg>`,
      },
      {
        key: 'nav.orders',
        path: '/orders',
        icon: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="9" y1="13" x2="15" y2="13"/>
          <line x1="9" y1="17" x2="15" y2="17"/>
          <polyline points="9 9 10 9 11 9"/>
        </svg>`,
      },
    ],
  },
  {
    labelKey: 'sidebar.data',
    items: [
      {
        key: 'nav.datasets',
        path: '/datasets',
        icon: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <ellipse cx="12" cy="5" rx="9" ry="3"/>
          <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/>
          <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/>
        </svg>`,
      },
    ],
  },
  {
    labelKey: 'sidebar.system',
    items: [
      {
        key: 'nav.settings',
        path: '/settings',
        icon: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
        </svg>`,
      },
    ],
  },
]
</script>

<template>
  <aside :class="['sidebar', { 'sidebar--collapsed': collapsed }]">

    <div class="brand">
      <div class="brand-logo">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
      </div>
      <Transition name="label">
        <div v-if="!collapsed" class="brand-text">
          <span class="brand-name">AI Assistant</span>
          <span class="brand-tag">Business Suite</span>
        </div>
      </Transition>
      <button class="collapse-btn" @click="collapsed = !collapsed">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
          :style="{ transform: collapsed ? 'rotate(180deg)' : 'none', transition: 'transform .25s' }">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
    </div>

    <div class="divider" />

    <nav class="nav">
      <template v-for="(group, gi) in menuGroups" :key="gi">
        <Transition name="label">
          <p v-if="!collapsed" class="nav-group-label">{{ t(group.labelKey) }}</p>
        </Transition>

        <router-link
          v-for="item in group.items"
          :key="item.path"
          :to="item.path"
          :class="['nav-link', { active: route.path === item.path }]"
          :title="collapsed ? t(item.key) : ''"
        >
          <span class="nav-icon" v-html="item.icon" />
          <Transition name="label">
            <span v-if="!collapsed" class="nav-label">{{ t(item.key) }}</span>
          </Transition>
        </router-link>

        <div v-if="gi < menuGroups.length - 1" class="group-sep" />
      </template>
    </nav>

    <div class="sidebar-bottom">
      <div class="divider" />
      <div class="version">
        <Transition name="label">
          <span v-if="!collapsed">v1.0 · beta</span>
          <span v-else>β</span>
        </Transition>
      </div>
    </div>

  </aside>
</template>

<style scoped>
.sidebar {
  width: 220px;
  height: 100%;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 1rem .65rem;
  transition: width .25s cubic-bezier(.4,0,.2,1);
  overflow: hidden;
  flex-shrink: 0;
}
.sidebar--collapsed { width: 60px; }

/* Brand */
.brand {
  display: flex;
  align-items: center;
  gap: .6rem;
  padding: .2rem .4rem .2rem .35rem;
  margin-bottom: .15rem;
}
.brand-logo {
  width: 32px; height: 32px;
  background: linear-gradient(135deg, var(--teal-dark), #0a3a3a);
  border: 1px solid var(--border-mid);
  border-radius: var(--r);
  display: flex; align-items: center; justify-content: center;
  color: var(--teal);
  flex-shrink: 0;
}
.brand-text {
  display: flex;
  flex-direction: column;
  gap: .05rem;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
}
.brand-name {
  font-size: .82rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -.02em;
  line-height: 1.2;
}
.brand-tag {
  font-size: .58rem;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: .04em;
  text-transform: uppercase;
  line-height: 1;
}
.collapse-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  width: 22px; height: 22px;
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s, color .15s;
  flex-shrink: 0;
}
.collapse-btn:hover { background: var(--bg-hover); color: var(--text-sub); }

/* Dividers */
.divider {
  height: 1px;
  background: var(--border);
  margin: .65rem 0;
}
.group-sep {
  height: 1px;
  background: var(--border-light);
  margin: .5rem 0;
}

/* Nav */
.nav {
  display: flex;
  flex-direction: column;
  gap: .05rem;
  flex: 1;
}
.nav-group-label {
  font-size: .58rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: .1em;
  text-transform: uppercase;
  padding: .35rem .6rem .2rem;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: .7rem;
  padding: .5rem .6rem;
  border-radius: var(--r);
  text-decoration: none;
  color: var(--text-muted);
  transition: background .15s, color .15s;
  position: relative;
  white-space: nowrap;
  overflow: hidden;
  font-size: .82rem;
  font-weight: 500;
}
.nav-link:hover  { background: var(--bg-hover); color: var(--text); }
.nav-link.active {
  background: var(--bg-hover);
  color: var(--text);
  border-left: 2px solid var(--teal);
  margin-left: -2px;
}

.nav-icon {
  width: 15px; height: 15px;
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.nav-label { font-size: .82rem; }

/* Bottom */
.sidebar-bottom { margin-top: auto; }
.version {
  font-size: .65rem;
  color: var(--text-muted);
  text-align: center;
  padding: .2rem;
  font-variant-numeric: tabular-nums;
}

/* Transitions */
.label-enter-active { transition: opacity .18s .04s, transform .18s .04s; }
.label-leave-active { transition: opacity .08s, transform .08s; }
.label-enter-from   { opacity: 0; transform: translateX(-5px); }
.label-leave-to     { opacity: 0; transform: translateX(-3px); }
</style>
