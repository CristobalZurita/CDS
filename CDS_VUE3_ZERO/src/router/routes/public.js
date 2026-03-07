const MasterLayout = () => import('@new/layouts/MasterLayout.vue')
const HomePage = () => import('@new/pages/public/HomePage.vue')
const LicensePage = () => import('@new/pages/public/LicensePage.vue')
const PolicyPage = () => import('@new/pages/public/PolicyPage.vue')
const TermsPage = () => import('@new/pages/public/TermsPage.vue')
const PrivacyPage = () => import('@new/pages/public/PrivacyPage.vue')
const SchedulePage = () => import('@new/pages/public/SchedulePage.vue')
const CotizadorIAPage = () => import('@new/pages/public/CotizadorIAPage.vue')
const CalculatorsPage = () => import('@new/pages/public/CalculatorsPage.vue')
const StorePage = () => import('@new/pages/public/StorePage.vue')

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
      { path: 'cotizador-ia', name: 'cotizador-ia', component: CotizadorIAPage, meta: { requiresAuth: false } },
      { path: 'calculadoras', name: 'calculadoras', component: CalculatorsPage, meta: { requiresAuth: false } },
      { path: 'tienda', name: 'tienda', component: StorePage, meta: { requiresAuth: false } }
    ]
  }
]
