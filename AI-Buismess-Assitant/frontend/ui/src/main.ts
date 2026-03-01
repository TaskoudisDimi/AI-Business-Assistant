import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './assets/main.css'   
import { i18n } from './i18n'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
const auth = useAuthStore()
await auth.initialize()

app.mount('#app')

