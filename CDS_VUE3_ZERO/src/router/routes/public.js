const MasterLayout = () => import('@/layouts/MasterLayout.vue')
const HomePage = () => import('@/pages/public/HomePage.vue')
const LicensePage = () => import('@/pages/public/LicensePage.vue')
const PolicyPage = () => import('@/pages/public/PolicyPage.vue')
const TermsPage = () => import('@/pages/public/TermsPage.vue')
const PrivacyPage = () => import('@/pages/public/PrivacyPage.vue')
const SchedulePage = () => import('@/pages/public/SchedulePage.vue')
const CotizadorIAPage = () => import('@/pages/public/CotizadorIAPage.vue')
const CalculatorsPage = () => import('@/pages/public/CalculatorsPage.vue')
const SimulatorPage = () => import('@/pages/public/SimulatorPage.vue')
const StorePage = () => import('@/pages/public/StorePage.vue')
const CartPage = () => import('@/pages/public/CartPage.vue')

export const publicRoutes = [
  {
    path: '/',
    component: MasterLayout,
    children: [
      { path: '', name: 'home', component: HomePage },
      { path: 'license', name: 'license', component: LicensePage },
      { path: 'policy', name: 'policy', component: PolicyPage },
      { path: 'terminos', name: 'terminos', component: TermsPage },
      { path: 'privacidad', name: 'privacidad', component: PrivacyPage },
      { path: 'agendar', name: 'agendar', component: SchedulePage, meta: { requiresAuth: true } },
      { path: 'cotizador', name: 'cotizador', component: CotizadorIAPage, meta: { requiresAuth: false } },
      { path: 'calculadoras', name: 'calculadoras', component: CalculatorsPage, meta: { requiresAuth: false } },
      { path: 'simulador', name: 'simulador', component: SimulatorPage, meta: { requiresAuth: false } },
      { path: 'tienda', name: 'tienda', component: StorePage, meta: { requiresAuth: false } },
      { path: 'carrito', name: 'carrito', component: CartPage, meta: { requiresAuth: false } }
    ]
  }
]
