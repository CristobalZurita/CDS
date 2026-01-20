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

// Allow mouse wheel to increment/decrement number inputs when hovered.
document.addEventListener(
  "wheel",
  (event) => {
    const target = event.target
    if (!(target instanceof HTMLInputElement)) return
    if (target.type !== "number") return
    if (document.activeElement !== target) {
      target.focus()
    }
    if (event.deltaY < 0) {
      target.stepUp()
    } else {
      target.stepDown()
    }
    event.preventDefault()
  },
  { passive: false }
)
