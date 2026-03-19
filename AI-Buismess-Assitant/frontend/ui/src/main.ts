// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router'
import { i18n } from './i18n'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)  // ← πρέπει να είναι εδώ, πριν app.use(pinia)

const app = createApp(App)
app.use(i18n)
app.use(pinia)                        // ← μετά το plugin
app.use(router)
app.mount('#app')