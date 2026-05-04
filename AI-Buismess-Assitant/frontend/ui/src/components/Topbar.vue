<script setup lang="ts">
import { computed, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const auth      = useAuthStore()
const route     = useRoute()
const router    = useRouter()

const showUserMenu = ref(false)
const showBizMenu  = ref(false)

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    "/dashboard": "Dashboard",
    "/sales":     "Sales Forecast",
    "/customers": "Customer Analysis",
    "/datasets":  "Datasets",
    "/settings":  "Settings",
  }
  return map[route.path] || "AI Assistant"
})

const pageSub = computed(() => {
  const map: Record<string, string> = {
    "/dashboard": "Επισκόπηση επιχείρησης",
    "/sales":     "Πρόβλεψη πωλήσεων",
    "/customers": "Ανάλυση πελατολογίου",
    "/datasets":  "Datasets & Ιστορικό",
    "/settings":  "Ρυθμίσεις λογαριασμού",
  }
  return map[route.path] || ""
})

const initials = computed(() => {
  const name = auth.user?.full_name ?? ""
  return name.split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2) || "U"
})

const logout = async () => {
  showUserMenu.value = false
  await auth.logout(router)
}

const switchBusiness = (id: string) => {
  auth.setCurrentBusiness(id)
  showBizMenu.value = false
}

const closeAll = () => {
  showUserMenu.value = false
  showBizMenu.value  = false
}
</script>

<template>
  <header class="topbar" @click="closeAll">

    <!-- Left: page title -->
    <div class="topbar-left">
      <h1 class="page-title">{{ pageTitle }}</h1>
      <span v-if="pageSub" class="page-sub">{{ pageSub }}</span>
    </div>

    <!-- Right: actions -->
    <div class="topbar-right" @click.stop>

      <!-- Business switcher -->
      <div v-if="auth.hasBusinesses" class="biz-wrap">
        <button class="biz-btn" @click="showBizMenu = !showBizMenu">
          <div class="biz-dot" />
          <span>{{ auth.currentBusiness?.name || 'Επιλογή' }}</span>
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
            :style="{ transform: showBizMenu ? 'rotate(180deg)' : 'none', transition: 'transform .2s' }">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </button>

        <Transition name="menu-pop">
          <div v-if="showBizMenu" class="dropdown">
            <p class="dropdown-label">Επιχειρήσεις</p>
            <button
              v-for="biz in auth.businesses"
              :key="biz.id"
              class="dropdown-item"
              :class="{ 'dropdown-item--active': biz.id === auth.currentBusinessId }"
              @click="switchBusiness(biz.id)"
            >
              <span class="dropdown-item-dot" :class="{ on: biz.id === auth.currentBusinessId }" />
              {{ biz.name }}
              <span v-if="biz.id === auth.currentBusinessId" class="current-tag">Τρέχον</span>
            </button>
          </div>
        </Transition>
      </div>

      <!-- Divider -->
      <div class="topbar-sep" />

      <!-- User -->
      <div class="user-wrap">
        <button class="user-btn" @click="showUserMenu = !showUserMenu">
          <div class="avatar">{{ initials }}</div>
          <span class="user-name">{{ auth.user?.full_name?.split(" ")[0] || "User" }}</span>
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
            :style="{ transform: showUserMenu ? 'rotate(180deg)' : 'none', transition: 'transform .2s' }">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </button>

        <Transition name="menu-pop">
          <div v-if="showUserMenu" class="dropdown dropdown--right">
            <div class="user-info">
              <div class="avatar avatar--lg">{{ initials }}</div>
              <div>
                <p class="user-info-name">{{ auth.user?.full_name }}</p>
                <p class="user-info-email">{{ auth.user?.email }}</p>
              </div>
            </div>
            <div class="dropdown-divider" />
            <button class="dropdown-item" @click="router.push('/settings'); showUserMenu = false">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
              Ρυθμίσεις
            </button>
            <div class="dropdown-divider" />
            <button class="dropdown-item dropdown-item--danger" @click="logout">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
              Αποσύνδεση
            </button>
          </div>
        </Transition>
      </div>

    </div>
  </header>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@400;500;600;700&display=swap');

.topbar {
  height: 64px;
  background: #060c18;
  border-bottom: 1px solid #0e1e33;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.75rem;
  font-family: 'Sora', sans-serif;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 20;
}

/* Left */
.topbar-left { display: flex; align-items: baseline; gap: .75rem; }
.page-title {
  font-size: 1rem;
  font-weight: 700;
  color: #c8daf5;
  margin: 0;
  letter-spacing: -.02em;
}
.page-sub {
  font-size: .72rem;
  color: #1e3a5a;
  font-family: 'DM Mono', monospace;
}

/* Right */
.topbar-right { display: flex; align-items: center; gap: .75rem; }
.topbar-sep { width: 1px; height: 24px; background: #0e1e33; }

/* Business button */
.biz-wrap { position: relative; }
.biz-btn {
  display: flex; align-items: center; gap: .5rem;
  background: #0a1525;
  border: 1px solid #122040;
  border-radius: 9px;
  color: #5a8acc;
  font-size: .78rem;
  font-weight: 500;
  font-family: 'Sora', sans-serif;
  padding: .4rem .8rem;
  cursor: pointer;
  transition: background .15s, border-color .15s;
  white-space: nowrap;
}
.biz-btn:hover { background: #0d1f38; border-color: #1a3460; color: #7ab0e0; }
.biz-dot {
  width: 6px; height: 6px;
  background: #3a9a60;
  border-radius: 50%;
  box-shadow: 0 0 6px #3a9a6088;
}

/* User button */
.user-wrap { position: relative; }
.user-btn {
  display: flex; align-items: center; gap: .5rem;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #5a8acc;
  font-family: 'Sora', sans-serif;
  padding: .3rem .4rem;
  border-radius: 9px;
  transition: background .15s;
}
.user-btn:hover { background: #0a1525; }
.user-name { font-size: .8rem; font-weight: 500; }

/* Avatar */
.avatar {
  width: 30px; height: 30px;
  background: linear-gradient(135deg, #1a3460, #0d244a);
  border: 1px solid #1e3a5f;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: .7rem; font-weight: 700; color: #7ab8ff;
  flex-shrink: 0;
}
.avatar--lg { width: 38px; height: 38px; font-size: .8rem; }

/* Dropdown shared */
.dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  background: #0a1525;
  border: 1px solid #122040;
  border-radius: 12px;
  padding: .4rem;
  min-width: 200px;
  z-index: 100;
  box-shadow: 0 16px 40px rgba(0,0,0,.6);
}
.dropdown--right { left: auto; right: 0; }

.dropdown-label {
  font-size: .65rem;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: #1e3a5a;
  padding: .35rem .6rem .2rem;
  font-family: 'DM Mono', monospace;
}
.dropdown-divider { height: 1px; background: #0e1e33; margin: .3rem 0; }

.dropdown-item {
  display: flex; align-items: center; gap: .55rem;
  width: 100%;
  background: transparent;
  border: none;
  color: #5a8acc;
  font-size: .8rem;
  font-family: 'Sora', sans-serif;
  padding: .5rem .65rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background .1s, color .1s;
  text-align: left;
}
.dropdown-item:hover { background: #0d1f38; color: #a0c8f0; }
.dropdown-item--active { background: #0d2040; color: #7ab8ff; }
.dropdown-item--danger { color: #7a3030; }
.dropdown-item--danger:hover { background: #1a0a0a; color: #f07070; }

.dropdown-item-dot {
  width: 5px; height: 5px;
  background: #1e3a5a;
  border-radius: 50%;
  flex-shrink: 0;
}
.dropdown-item-dot.on { background: #3a9a60; box-shadow: 0 0 6px #3a9a6088; }

.current-tag {
  margin-left: auto;
  background: #0d2a1a;
  border: 1px solid #1a4a30;
  color: #3a9a60;
  font-size: .65rem;
  padding: .1rem .45rem;
  border-radius: 999px;
  font-family: 'DM Mono', monospace;
}

/* User info header */
.user-info {
  display: flex; align-items: center; gap: .75rem;
  padding: .5rem .65rem .65rem;
}
.user-info-name { font-size: .82rem; font-weight: 600; color: #a0c0e8; margin: 0; }
.user-info-email { font-size: .7rem; color: #2a4060; margin: .1rem 0 0; font-family: 'DM Mono', monospace; }

/* Transitions */
.menu-pop-enter-active { transition: all .15s cubic-bezier(.2,.8,.3,1); }
.menu-pop-leave-active { transition: all .1s ease; }
.menu-pop-enter-from { opacity: 0; transform: scale(.93) translateY(-6px); }
.menu-pop-leave-to   { opacity: 0; transform: scale(.96); }

@media (max-width: 640px) {
  .page-sub, .user-name { display: none; }
  .topbar { padding: 0 1rem; }
}
</style>