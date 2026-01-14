/**
 * Router - Vue Router configuration
 * Define todas las rutas de la aplicación
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Layouts
import Master from '@/vue/content/Master.vue'

// Pages
import HomePage from '@/vue/content/pages/HomePage.vue'
import LoginPage from '@/vue/content/pages/LoginPage.vue'
import RegisterPage from '@/vue/content/pages/RegisterPage.vue'
import DashboardPage from '@/vue/content/pages/DashboardPage.vue'
import RepairsPage from '@/vue/content/pages/RepairsPage.vue'
import ProfilePage from '@/vue/content/pages/ProfilePage.vue'
import CotizadorIAPage from '@/vue/content/pages/CotizadorIAPage.vue'
import LicensePage from '@/vue/content/pages/LicensePage.vue'
import PolicyPage from '@/vue/content/pages/PolicyPage.vue'
import TermsPage from '@/vue/content/pages/TermsPage.vue'
import PrivacyPage from '@/vue/content/pages/PrivacyPage.vue'
import SchedulePage from '@/vue/content/pages/SchedulePage.vue'

// Admin Pages
import AdminDashboard from '@/vue/content/pages/admin/AdminDashboard.vue'
import InventoryPage from '@/vue/content/pages/admin/InventoryPage.vue'
import InventoryUnified from '@/views/InventoryUnified.vue'
import ClientsPage from '@/vue/content/pages/admin/ClientsPage.vue'
import RepairsAdminPage from '@/vue/content/pages/admin/RepairsAdminPage.vue'
import StatsPage from '@/vue/content/pages/admin/StatsPage.vue'
import CategoriesPage from '@/vue/content/pages/admin/CategoriesPage.vue'

const routes = [
  // Public routes
  {
    path: '/',
    component: Master,
    children: [
      {
        path: '',
        name: 'home',
        component: HomePage
      },
      {
        path: 'license',
        name: 'license',
        component: LicensePage
      },
      {
        path: 'policy',
        name: 'policy',
        component: PolicyPage
      },
      {
        path: 'terminos',
        name: 'terminos',
        component: TermsPage
      },
      {
        path: 'privacidad',
        name: 'privacidad',
        component: PrivacyPage
      },
      {
        path: 'agendar',
        name: 'agendar',
        component: SchedulePage,
        meta: { requiresAuth: true }
      },
      {
        path: 'cotizador-ia',
        name: 'cotizador-ia',
        component: CotizadorIAPage,
        meta: { requiresAuth: false }
      }
    ]
  },

  // Auth routes
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { requiresAuth: false, requiresGuest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
    meta: { requiresAuth: false, requiresGuest: true }
  },

  // Client routes (requieren autenticación)
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/repairs',
    name: 'repairs',
    component: RepairsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfilePage,
    meta: { requiresAuth: true }
  },

  // Admin routes (requieren autenticación y rol admin)
  {
    path: '/admin',
    component: Master,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'admin-dashboard',
        component: AdminDashboard
      },
      {
        path: 'inventory',
        name: 'admin-inventory',
        component: InventoryPage
      },
      {
        path: 'inventory/unified',
        name: 'admin-inventory-unified',
        component: InventoryUnified
      },
      {
        path: 'clients',
        name: 'admin-clients',
        component: ClientsPage
      },
      {
        path: 'repairs',
        name: 'admin-repairs',
        component: RepairsAdminPage
      },
      {
        path: 'stats',
        name: 'admin-stats',
        component: StatsPage
      },
      {
        path: 'categories',
        name: 'admin-categories',
        component: CategoriesPage
      }
    ]
  },

  // 404 - Ruta no encontrada
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),
  routes
})

/**
 * Navigation guards - Proteger rutas según autenticación
 */
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Verificar autenticación si no está hecho aún
  if (!authStore.token && to.meta.requiresAuth) {
    // Intentar recuperar sesión del localStorage
    await authStore.checkAuth()
  }

  // Ruta requiere autenticación
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // Ruta requiere rol admin
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'home' })
    return
  }

  // Ruta requiere que NO esté autenticado (login, register)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
    return
  }

  next()
})

export default router
