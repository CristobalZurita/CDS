/**
 * Router - Vue Router configuration
 * Define todas las rutas de la aplicación
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Layouts
import Master from '@/vue/content/Master.vue'

// Lazy load pages (code splitting) - use modern arrow function syntax
const HomePage = () => import('@/vue/content/pages/HomePage.vue')
const LoginPage = () => import('@/vue/content/pages/LoginPage.vue')
const RegisterPage = () => import('@/vue/content/pages/RegisterPage.vue')
const PasswordResetPage = () => import('@/vue/content/pages/PasswordResetPage.vue')
const DashboardPage = () => import('@/vue/content/pages/DashboardPage.vue')
const RepairsPage = () => import('@/vue/content/pages/RepairsPage.vue')
const RepairDetailPage = () => import('@/vue/content/pages/RepairDetailPage.vue')
const ProfilePage = () => import('@/vue/content/pages/ProfilePage.vue')
const CotizadorIAPage = () => import('@/vue/content/pages/CotizadorIAPage.vue')
const LicensePage = () => import('@/vue/content/pages/LicensePage.vue')
const PolicyPage = () => import('@/vue/content/pages/PolicyPage.vue')
const TermsPage = () => import('@/vue/content/pages/TermsPage.vue')
const PrivacyPage = () => import('@/vue/content/pages/PrivacyPage.vue')
const SchedulePage = () => import('@/vue/content/pages/SchedulePage.vue')
const CalculatorsPage = () => import('@/vue/content/pages/CalculatorsPage.vue')

// Admin Pages - lazy load
const AdminDashboard = () => import('@/vue/content/pages/admin/AdminDashboard.vue')
const InventoryPage = () => import('@/vue/content/pages/admin/InventoryPage.vue')
const InventoryUnified = () => import('@/views/InventoryUnified.vue')
const ClientsPage = () => import('@/vue/content/pages/admin/ClientsPage.vue')
const RepairsAdminPage = () => import('@/vue/content/pages/admin/RepairsAdminPage.vue')
const CategoriesPage = () => import('@/vue/content/pages/admin/CategoriesPage.vue')
const ContactMessagesPage = () => import('@/vue/content/pages/admin/ContactMessagesPage.vue')
const NewsletterSubscriptionsPage = () => import('@/vue/content/pages/admin/NewsletterSubscriptionsPage.vue')
const AppointmentsPage = () => import('@/vue/content/pages/admin/AppointmentsPage.vue')
const RepairDetailAdminPage = () => import('@/vue/content/pages/admin/RepairDetailAdminPage.vue')
const TicketsPage = () => import('@/vue/content/pages/admin/TicketsPage.vue')
const PurchaseRequestsPage = () => import('@/vue/content/pages/admin/PurchaseRequestsPage.vue')
const ArchivePage = () => import('@/vue/content/pages/admin/ArchivePage.vue')
const SignaturePage = () => import('@/vue/content/pages/SignaturePage.vue')
const PhotoUploadPage = () => import('@/vue/content/pages/PhotoUploadPage.vue')

const routes: RouteRecordRaw[] = [
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
      },
      {
        path: 'calculadoras',
        name: 'calculadoras',
        component: CalculatorsPage,
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
        path: 'repairs/:id',
        name: 'admin-repair-detail',
        component: RepairDetailAdminPage
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
      },
      {
        path: 'appointments',
        name: 'admin-appointments',
        component: AppointmentsPage
      },
      {
        path: 'tickets',
        name: 'admin-tickets',
        component: TicketsPage
      },
      {
        path: 'purchase-requests',
        name: 'admin-purchase-requests',
        component: PurchaseRequestsPage
      },
      {
        path: 'archive',
        name: 'admin-archive',
        component: ArchivePage
      },
      {
        path: 'manuals',
        redirect: '/admin/archive'
      }
    ]
  },
  {
    path: '/signature/:token',
    name: 'signature',
    component: SignaturePage,
    meta: { requiresAuth: false }
  },
  {
    path: '/photo-upload/:token',
    name: 'photo-upload',
    component: PhotoUploadPage,
    meta: { requiresAuth: false }
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
  history: createWebHistory(import.meta.env.BASE_URL as string || '/'),
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
