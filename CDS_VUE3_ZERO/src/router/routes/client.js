const DashboardPage = () => import('@/pages/client/DashboardPage.vue')
const OtPaymentsPage = () => import('@/pages/client/OtPaymentsPage.vue')
const RepairsPage = () => import('@/pages/client/RepairsPage.vue')
const RepairDetailPage = () => import('@/pages/client/RepairDetailPage.vue')
const ProfilePage = () => import('@/pages/client/ProfilePage.vue')
const PaymentResultPage = () => import('@/pages/client/PaymentResultPage.vue')

export const clientRoutes = [
  { path: '/dashboard', name: 'dashboard', component: DashboardPage, meta: { requiresAuth: true } },
  { path: '/ot-payments', name: 'ot-payments', component: OtPaymentsPage, meta: { requiresAuth: true } },
  { path: '/repairs', name: 'repairs', component: RepairsPage, meta: { requiresAuth: true } },
  { path: '/repairs/:id', name: 'repair-detail', component: RepairDetailPage, meta: { requiresAuth: true } },
  { path: '/profile', name: 'profile', component: ProfilePage, meta: { requiresAuth: true } },
  { path: '/pago/resultado', name: 'payment-result', component: PaymentResultPage, meta: { requiresAuth: true } },
]
