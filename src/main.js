// SASS Architecture - main.scss es el nuevo entry point
// Si hay problemas, cambiar a: import "./scss/style.scss"
import "./scss/main.scss"
import "./assets/styles/tokens.css"
import { createApp } from "vue"
import { createPinia } from "pinia"
import App from "/src/vue/stack/App.vue"
import router from "@/router"
import { useAuthStore } from "@/stores/auth"
import { initAnalytics, track } from "@/analytics"
import { AnalyticsEvents } from "@/analytics/events"

const app = createApp(App)

// Install Pinia for state management
const pinia = createPinia()
app.use(pinia)

// Install Vue Router
app.use(router)

// Initialize auth on app startup
const authStore = useAuthStore()
authStore.checkAuth()

// Analytics: page view tracking (GA4/GTM)
initAnalytics()
const gaId = import.meta.env.VITE_GA_ID
if (gaId && !window.__gaLoaded) {
  window.__gaLoaded = true
  window.dataLayer = window.dataLayer || []
  const gtagScript = document.createElement("script")
  gtagScript.async = true
  gtagScript.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`
  document.head.appendChild(gtagScript)
  window.gtag = function gtag() {
    window.dataLayer.push(arguments)
  }
  window.gtag("js", new Date())
  window.gtag("config", gaId)
}
router.afterEach((to) => {
  track(AnalyticsEvents.PAGE_VIEW, {
    path: to.fullPath,
    name: to.name || ''
  })
})

// Mount app
app.mount("#app")

if ("serviceWorker" in navigator && import.meta.env.PROD) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {
      // Keep silent: no hard failure for SW registration
    })
  })
}

if ("serviceWorker" in navigator && import.meta.env.DEV) {
  navigator.serviceWorker.getRegistrations().then((registrations) => {
    registrations.forEach((registration) => {
      registration.unregister().catch(() => {
        // Keep silent in dev cleanup
      })
    })
  })

  if ("caches" in window) {
    caches.keys().then((keys) => {
      keys
        .filter((key) => key.startsWith("cds-"))
        .forEach((key) => caches.delete(key).catch(() => {
          // Keep silent in dev cleanup
        }))
    })
  }
}

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
