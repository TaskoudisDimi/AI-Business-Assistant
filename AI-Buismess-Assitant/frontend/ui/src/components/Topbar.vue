<script setup lang="ts">
import { computed, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"


const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const showMenu = ref(false)

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    "/dashboard": "Dashboard",
    "/sales": "Sales Forecast",
    "/customers": "Customer Analysis",
    "/marketing": "Marketing AI",
    "/datasets": "Datasets",
    "/history": "History",
    "/settings": "Settings"
  }

  return map[route.path] || "AI Assistant"
})

const logout = async () => {
  await auth.logout(router)
}

const authStore = useAuthStore()

const switchBusiness = (id: string) => {
  authStore.setCurrentBusiness(id)
  router.push(router.currentRoute.value.path) 
}

</script>

<template>
  <header class="topbar">
    <!-- CENTER -->
    <div class="center">
      <input placeholder="Search..." />
    </div>
    <div v-if="authStore.hasBusinesses" class="dropdown dropdown-end">
        <label tabindex="0" class="btn btn-ghost">
          <span class="font-medium">
            {{ authStore.currentBusiness?.name || 'Επιλογή επιχείρησης' }}
          </span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </label>
        <ul tabindex="0" class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52">
          <li v-for="biz in authStore.businesses" :key="biz.id">
            <a @click="switchBusiness(biz.id)" :class="{ 'bg-base-200': biz.id === authStore.currentBusinessId }">
              {{ biz.name }}
              <span v-if="biz.id === authStore.currentBusinessId" class="badge badge-sm badge-success ml-auto">Τρέχον</span>
            </a>
          </li>
        </ul>
      </div>


    <!-- RIGHT -->
    <div class="right">
      <div class="user" @click="showMenu = !showMenu">
        <div class="avatar">
          {{ auth.user?.full_name?.charAt(0) || "U" }}
        </div>
        <span class="name">
          {{ auth.user?.full_name || "User" }}
        </span>
      </div>

      <div v-if="showMenu" class="dropdown">
        <button @click="router.push('/settings')">Settings</button>
        <button @click="logout">Logout</button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  height: 70px;
  background: #111827;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  border-bottom: 1px solid #1f2937;
  position: relative;
}

.left h2 {
  font-size: 1.2rem;
  font-weight: 600;
}

.center input {
  width: 300px;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #1e293b;
  color: white;
}

.center input:focus {
  outline: none;
  border-color: #3b82f6;
}

.right {
  position: relative;
}

.user {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.avatar {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.name {
  font-size: 0.9rem;
}

.dropdown {
  position: absolute;
  top: 55px;
  right: 0;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  min-width: 150px;
}

.dropdown button {
  background: none;
  border: none;
  color: white;
  padding: 8px;
  text-align: left;
  cursor: pointer;
  border-radius: 6px;
}

.dropdown button:hover {
  background: #334155;
}

/* Responsive */
@media (max-width: 900px) {
  .center {
    display: none;
  }

  .name {
    display: none;
  }
}
</style>