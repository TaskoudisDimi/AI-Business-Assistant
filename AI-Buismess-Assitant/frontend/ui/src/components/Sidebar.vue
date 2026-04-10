<script setup lang="ts">
import { ref } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()
const collapsed = ref(false)

const menu = [
  { name: "Dashboard",         path: "/dashboard", icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>` },
  { name: "Sales Forecast",    path: "/sales",     icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>` },
  { name: "Customer Analysis", path: "/customers", icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>` },
  { name: "Marketing AI",      path: "/marketing", icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>` },
  { name: "Datasets",          path: "/datasets",  icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/></svg>` },
  { name: "History",           path: "/history",   icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>` },
  { name: "Settings",          path: "/settings",  icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>` },
]
</script>

<template>
  <aside :class="['sidebar', { 'sidebar--collapsed': collapsed }]">

    <!-- Brand -->
    <div class="sidebar-brand">
      <div class="brand-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
      </div>
      <Transition name="fade-label">
        <span v-if="!collapsed" class="brand-name">AI Assistant</span>
      </Transition>
      <button class="collapse-btn" @click="collapsed = !collapsed" :title="collapsed ? 'Expand' : 'Collapse'">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
          :style="{ transform: collapsed ? 'rotate(180deg)' : 'none', transition: 'transform .3s' }">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
    </div>

    <!-- Divider -->
    <div class="sidebar-divider" />

    <!-- Nav -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in menu"
        :key="item.path"
        :to="item.path"
        class="nav-link"
        :class="{ 'nav-link--active': route.path === item.path }"
        :title="collapsed ? item.name : ''"
      >
        <span class="nav-icon" v-html="item.icon" />
        <Transition name="fade-label">
          <span v-if="!collapsed" class="nav-label">{{ item.name }}</span>
        </Transition>
        <span v-if="!collapsed && route.path === item.path" class="active-pip" />
      </router-link>
    </nav>

    <!-- Bottom -->
    <div class="sidebar-bottom">
      <div class="sidebar-divider" />
      <div class="version-tag">
        <Transition name="fade-label">
          <span v-if="!collapsed">v1.0 · beta</span>
          <span v-else>β</span>
        </Transition>
      </div>
    </div>

  </aside>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&display=swap');

.sidebar {
  width: 240px;
  min-height: 100vh;
  background: #060c18;
  border-right: 1px solid #0e1e33;
  display: flex;
  flex-direction: column;
  padding: 1.25rem .75rem;
  transition: width .3s cubic-bezier(.4,0,.2,1);
  overflow: hidden;
  font-family: 'Sora', sans-serif;
  flex-shrink: 0;
}
.sidebar--collapsed { width: 68px; }

/* Brand */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: .65rem;
  padding: .25rem .5rem .25rem .4rem;
  margin-bottom: .25rem;
  position: relative;
}
.brand-icon {
  width: 34px; height: 34px;
  background: linear-gradient(135deg, #1a3460 0%, #0d1f3e 100%);
  border: 1px solid #1e3a5f;
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  color: #4a9eff;
  flex-shrink: 0;
}
.brand-name {
  font-size: .9rem;
  font-weight: 700;
  color: #c8daf5;
  letter-spacing: -.02em;
  white-space: nowrap;
  flex: 1;
}
.collapse-btn {
  background: transparent;
  border: none;
  color: #2a4060;
  cursor: pointer;
  width: 24px; height: 24px;
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s, color .15s;
  flex-shrink: 0;
}
.collapse-btn:hover { background: #0e1e33; color: #5a8acc; }

/* Divider */
.sidebar-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #0e1e33 30%, #0e1e33 70%, transparent);
  margin: .75rem 0;
}

/* Nav */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: .2rem;
  flex: 1;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: .75rem;
  padding: .6rem .65rem;
  border-radius: 9px;
  text-decoration: none;
  color: #3a5a80;
  transition: background .15s, color .15s;
  position: relative;
  white-space: nowrap;
  overflow: hidden;
}
.nav-link:hover {
  background: #0a1828;
  color: #7ab0e0;
}
.nav-link--active {
  background: #0d2040;
  color: #7ab8ff;
}
.nav-icon {
  width: 16px; height: 16px;
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.nav-label {
  font-size: .82rem;
  font-weight: 500;
}
.active-pip {
  position: absolute;
  right: .6rem;
  width: 5px; height: 5px;
  background: #4a9eff;
  border-radius: 50%;
  box-shadow: 0 0 8px #4a9eff88;
}

/* Bottom */
.sidebar-bottom { margin-top: auto; }
.version-tag {
  font-size: .68rem;
  color: #1a3050;
  text-align: center;
  padding: .25rem;
  font-family: 'DM Mono', monospace;
}

/* Transitions */
.fade-label-enter-active { transition: opacity .2s .05s, transform .2s .05s; }
.fade-label-leave-active { transition: opacity .1s, transform .1s; }
.fade-label-enter-from   { opacity: 0; transform: translateX(-6px); }
.fade-label-leave-to     { opacity: 0; transform: translateX(-4px); }
</style>