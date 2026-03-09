import { createRouter, createWebHistory } from 'vue-router'
import { appRoutes } from './routes'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),
  routes: appRoutes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const routeDependsOnSession = Boolean(to.meta.requiresAuth || to.meta.requiresGuest || to.meta.requiresAdmin)
  const shouldHydrateSession = routeDependsOnSession && (!authStore.isAuthenticated || !authStore.user)

  if (shouldHydrateSession) {
    await authStore.checkAuth()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'home' })
    return
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
    return
  }

  next()
})

export default router
