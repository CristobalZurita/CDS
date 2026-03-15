import { createApp } from 'vue'
import { createPinia } from 'pinia'
import VueApexCharts from 'vue3-apexcharts'
import AppRoot from '@/app/AppRoot.vue'
import router from '@/router'
import '@/styles/main.css'

const app = createApp(AppRoot)
app.use(createPinia())
app.use(router)
app.use(VueApexCharts)
app.mount('#app')
