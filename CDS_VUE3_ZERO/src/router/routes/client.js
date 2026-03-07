const DashboardPage = () => import('@new/pages/client/DashboardPage.vue')
const OtPaymentsPage = () => import('@new/pages/client/OtPaymentsPage.vue')
const RepairsPage = () => import('@new/pages/client/RepairsPage.vue')
const RepairDetailPage = () => import('@new/pages/client/RepairDetailPage.vue')
const ProfilePage = () => import('@new/pages/client/ProfilePage.vue')

export const clientRoutes = [
  { path: '/dashboard', name: 'dashboard', component: DashboardPage, meta: { requiresAuth: true } },
  { path: '/ot-payments', name: 'ot-payments', component: OtPaymentsPage, meta: { requiresAuth: true } },
  { path: '/repairs', name: 'repairs', component: RepairsPage, meta: { requiresAuth: true } },
  { path: '/repairs/:id', name: 'repair-detail', component: RepairDetailPage, meta: { requiresAuth: true } },
  { path: '/profile', name: 'profile', component: ProfilePage, meta: { requiresAuth: true } }
]
