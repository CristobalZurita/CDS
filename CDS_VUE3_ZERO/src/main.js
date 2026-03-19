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
