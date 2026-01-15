import "./scss/style.scss"
import "@fortawesome/fontawesome-free/css/all.css"
import { createApp } from "vue"
import { createPinia } from "pinia"
import App from "/src/vue/stack/App.vue"
import router from "@/router"
import { useAuthStore } from "@/stores/auth"

const app = createApp(App)

// Install Pinia for state management
const pinia = createPinia()
app.use(pinia)

// Install Vue Router
app.use(router)

// Initialize auth on app startup
const authStore = useAuthStore()
authStore.checkAuth()

// Mount app
app.mount("#app")
