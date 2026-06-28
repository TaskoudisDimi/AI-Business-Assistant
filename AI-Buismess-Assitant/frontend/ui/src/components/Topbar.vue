<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { setLocale } from '@/i18n'

const auth   = useAuthStore()
const route  = useRoute()
const router = useRouter()
const { t, locale } = useI18n()

const toggleLocale = () => {
  const next = locale.value === 'el' ? 'en' : 'el'
  setLocale(next as 'el' | 'en')
}

const showUserMenu = ref(false)

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    '/dashboard': t('nav.dashboard'),
    '/sales':     t('nav.salesForecast'),
    '/customers': t('nav.customerAnalysis'),
    '/datasets':  t('nav.datasets'),
    '/settings':  t('nav.settings'),
    '/inventory': t('nav.inventory'),
    '/products':  t('nav.products'),
    '/orders':    t('nav.orders'),
  }
  return map[route.path] || 'AI Assistant'
})

const pageSub = computed(() => {
  const map: Record<string, string> = {
    '/dashboard': t('topbar.sub.dashboard'),
    '/sales':     t('topbar.sub.sales'),
    '/customers': t('topbar.sub.customers'),
    '/datasets':  t('topbar.sub.datasets'),
    '/settings':  t('topbar.sub.settings'),
    '/inventory': t('topbar.sub.inventory'),
    '/products':  t('topbar.sub.products'),
    '/orders':    t('topbar.sub.orders'),
  }
  return map[route.path] || ''
})

const initials = computed(() => {
  const name = auth.user?.full_name ?? ''
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) || 'U'
})

const logout = async () => {
  showUserMenu.value = false
  await auth.logout(router)
}

const closeAll = () => {
  showUserMenu.value = false
}
</script>

<template>
  <header class="topbar" @click="closeAll">

    <div class="topbar-left">
      <h1 class="page-title">{{ pageTitle }}</h1>
      <span v-if="pageSub" class="page-sub">{{ pageSub }}</span>
    </div>

    <div class="topbar-right" @click.stop>

      <!-- Language toggle -->
      <button class="lang-btn" @click="toggleLocale" :title="locale === 'el' ? 'Switch to English' : 'Αλλαγή σε Ελληνικά'">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
        </svg>
        <span>{{ locale === 'el' ? 'EN' : 'EL' }}</span>
      </button>

      <div class="sep" />

      <!-- User menu -->
      <div class="dropdown-host">
        <button class="user-btn" @click="showUserMenu = !showUserMenu">
          <div class="avatar">{{ initials }}</div>
          <span class="user-name">{{ auth.user?.full_name?.split(' ')[0] || 'User' }}</span>
          <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
            :style="{ transform: showUserMenu ? 'rotate(180deg)' : '', transition: 'transform .2s' }">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </button>

        <Transition name="menu-pop">
          <div v-if="showUserMenu" class="dropdown dropdown--right">
            <div class="user-info">
              <div class="avatar avatar--lg">{{ initials }}</div>
              <div>
                <p class="user-name-full">{{ auth.user?.full_name }}</p>
                <p class="user-email">{{ auth.user?.email }}</p>
              </div>
            </div>
            <div class="dropdown-divider" />
            <button class="dropdown-item" @click="router.push('/settings'); showUserMenu = false">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
              </svg>
              {{ t('nav.settings') }}
            </button>
            <div class="dropdown-divider" />
            <button class="dropdown-item dropdown-item--danger" @click="logout">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
              {{ t('auth.logout') }}
            </button>
          </div>
        </Transition>
      </div>

    </div>
  </header>
</template>

<style scoped>
.topbar {
  height: 56px;
  background: var(--bg-sidebar);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 20;
}

.topbar-left { display: flex; align-items: baseline; gap: .65rem; }
.page-title  { font-size: .95rem; font-weight: 600; color: var(--text); margin: 0; letter-spacing: -.01em; }
.page-sub    { font-size: .72rem; color: var(--text-muted); }

.topbar-right { display: flex; align-items: center; gap: .6rem; }
.sep { width: 1px; height: 20px; background: var(--border); }

/* Language toggle */
.lang-btn {
  display: flex; align-items: center; gap: .3rem;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--r);
  color: var(--text-muted);
  font-size: .72rem;
  font-weight: 600;
  padding: .28rem .55rem;
  cursor: pointer;
  letter-spacing: .04em;
  transition: border-color .15s, color .15s;
}
.lang-btn:hover { border-color: var(--border-mid); color: var(--teal); }

/* Business */
.dropdown-host { position: relative; }
.biz-btn {
  display: flex; align-items: center; gap: .45rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r);
  color: var(--text-sub);
  font-size: .78rem;
  font-weight: 500;
  padding: .35rem .7rem;
  cursor: pointer;
  transition: border-color .15s, color .15s;
  white-space: nowrap;
}
.biz-btn:hover { border-color: var(--border-mid); color: var(--text); }

.online-dot {
  width: 6px; height: 6px;
  background: var(--green);
  border-radius: 50%;
  flex-shrink: 0;
}

/* User */
.user-btn {
  display: flex; align-items: center; gap: .45rem;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-sub);
  padding: .3rem .35rem;
  border-radius: var(--r);
  transition: background .15s;
}
.user-btn:hover { background: var(--bg-hover); }
.user-name { font-size: .8rem; font-weight: 500; color: var(--text-sub); }

/* Avatar */
.avatar {
  width: 28px; height: 28px;
  background: linear-gradient(135deg, var(--teal-dark), #0a3a3a);
  border: 1px solid var(--border-mid);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: .68rem; font-weight: 700; color: var(--teal);
  flex-shrink: 0;
}
.avatar--lg { width: 36px; height: 36px; font-size: .78rem; }

/* Dropdown */
.dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  background: var(--bg-card);
  border: 1px solid var(--border-mid);
  border-radius: var(--r-lg);
  padding: .35rem;
  min-width: 190px;
  z-index: 100;
  box-shadow: var(--shadow-lg);
}
.dropdown--right { left: auto; right: 0; }

.dropdown-label {
  font-size: .64rem;
  font-weight: 600;
  letter-spacing: .07em;
  text-transform: uppercase;
  color: var(--text-muted);
  padding: .3rem .55rem .2rem;
}
.dropdown-divider { height: 1px; background: var(--border); margin: .25rem 0; }

.dropdown-item {
  display: flex; align-items: center; gap: .5rem;
  width: 100%;
  background: transparent;
  border: none;
  color: var(--text-sub);
  font-size: .8rem;
  padding: .45rem .6rem;
  border-radius: var(--r);
  cursor: pointer;
  transition: background .1s, color .1s;
  text-align: left;
}
.dropdown-item:hover         { background: var(--bg-hover); color: var(--text); }
.dropdown-item--active       { background: var(--bg-hover); color: var(--text); }
.dropdown-item--danger       { color: var(--red); }
.dropdown-item--danger:hover { background: var(--red-bg); }

.item-dot {
  width: 5px; height: 5px;
  background: var(--text-muted);
  border-radius: 50%;
  flex-shrink: 0;
}
.item-dot.on { background: var(--green); }

.current-tag {
  margin-left: auto;
  background: var(--green-bg);
  border: 1px solid rgba(58,184,122,.25);
  color: var(--green);
  font-size: .63rem;
  padding: .08rem .4rem;
  border-radius: 999px;
}

.user-info {
  display: flex; align-items: center; gap: .65rem;
  padding: .45rem .6rem .55rem;
}
.user-name-full { font-size: .82rem; font-weight: 600; color: var(--text); margin: 0; }
.user-email     { font-size: .7rem; color: var(--text-muted); margin: .06rem 0 0; }

/* Transitions */
.menu-pop-enter-active { transition: all .14s cubic-bezier(.2,.8,.3,1); }
.menu-pop-leave-active { transition: all .1s ease; }
.menu-pop-enter-from   { opacity: 0; transform: scale(.94) translateY(-5px); }
.menu-pop-leave-to     { opacity: 0; transform: scale(.97); }

@media (max-width: 640px) {
  .page-sub, .user-name { display: none; }
  .topbar { padding: 0 1rem; }
}
</style>
