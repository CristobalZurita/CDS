import { createApp } from 'vue'
import { createPinia } from 'pinia'
import AppRoot from '@/app/AppRoot.vue'
import { VueQueryPlugin, vueQueryPluginOptions } from '@/plugins/vueQuery'
import router from '@/router'
import '@/styles/main.css'

const app = createApp(AppRoot)
app.use(createPinia())
app.use(VueQueryPlugin, vueQueryPluginOptions)
app.use(router)
app.mount('#app')

// Registrar service worker para PWA (solo en produccion)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
  })
}
