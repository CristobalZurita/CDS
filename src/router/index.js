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
import PasswordResetPage from '@/vue/content/pages/PasswordResetPage.vue'
import DashboardPage from '@/vue/content/pages/DashboardPage.vue'
import RepairsPage from '@/vue/content/pages/RepairsPage.vue'
import RepairDetailPage from '@/vue/content/pages/RepairDetailPage.vue'
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
import ContactMessagesPage from '@/vue/content/pages/admin/ContactMessagesPage.vue'
import NewsletterSubscriptionsPage from '@/vue/content/pages/admin/NewsletterSubscriptionsPage.vue'

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
  {
    path: '/password-reset',
    name: 'password-reset',
    component: PasswordResetPage,
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
    path: '/repairs/:id',
    name: 'repair-detail',
    component: RepairDetailPage,
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
      },
      {
        path: 'contact',
        name: 'admin-contact',
        component: ContactMessagesPage
      },
      {
        path: 'newsletter',
        name: 'admin-newsletter',
        component: NewsletterSubscriptionsPage
      }
    ]
  },

  // Calculadoras electrónicas (rutas públicas con lazy loading)
  {
    path: '/calc/555',
    name: 'calc-555',
    component: () => import('@/modules/timer555/Timer555View.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/calc/resistor-color',
    name: 'calc-resistor-color',
    component: () => import('@/modules/resistorColor/ResistorColorView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/calc/smd-capacitor',
    name: 'calc-smd-capacitor',
    component: () => import('@/modules/smdCapacitor/SmdCapacitorView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/calc/smd-resistor',
    name: 'calc-smd-resistor',
    component: () => import('@/modules/smdResistor/SmdResistorView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/calc/ohms-law',
    name: 'calc-ohms-law',
    component: () => import('@/modules/ohmsLaw/OhmsLawView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/calc/temperature',
    name: 'calc-temperature',
    component: () => import('@/modules/temperature/TemperatureView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/calc/number-system',
    name: 'calc-number-system',
    component: () => import('@/modules/numberSystem/NumberSystemView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/calc/length',
    name: 'calc-length',
    component: () => import('@/modules/length/LengthView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/calc/awg',
    name: 'calc-awg',
    component: () => import('@/modules/awg/AwgView.vue'),
    meta: { requiresAuth: false }
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
