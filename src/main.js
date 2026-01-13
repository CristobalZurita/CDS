import "./scss/style.scss"
import "@fortawesome/fontawesome-free/css/all.css"
import { createApp } from "vue"
import { createPinia } from "pinia"
import App from "@/vue/stack/App.vue"
import router from "@/router"

const app = createApp(App)

// Install Pinia FIRST - before creating stores
const pinia = createPinia()
app.use(pinia)

// Install Vue Router
app.use(router)

// Mount app
app.mount("#app")
