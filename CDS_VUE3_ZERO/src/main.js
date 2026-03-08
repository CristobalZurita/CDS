import { createApp } from 'vue'
import { createPinia } from 'pinia'
import AppRoot from '@new/app/AppRoot.vue'
import router from '@new/router'
import '@fortawesome/fontawesome-free/css/fontawesome.min.css'
import '@fortawesome/fontawesome-free/css/solid.min.css'
import '@fortawesome/fontawesome-free/css/brands.min.css'
import '@new/styles/main.css'

const app = createApp(AppRoot)
app.use(createPinia())
app.use(router)
app.mount('#app')
