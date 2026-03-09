const LoginPage = () => import('@/pages/auth/LoginPage.vue')
const RegisterPage = () => import('@/pages/auth/RegisterPage.vue')
const PasswordResetPage = () => import('@/pages/auth/PasswordResetPage.vue')

export const authRoutes = [
  { path: '/login', name: 'login', component: LoginPage, meta: { requiresAuth: false, requiresGuest: true } },
  { path: '/register', name: 'register', component: RegisterPage, meta: { requiresAuth: false, requiresGuest: true } },
  { path: '/registro', redirect: '/register' },
  { path: '/password-reset', name: 'password-reset', component: PasswordResetPage, meta: { requiresAuth: false, requiresGuest: true } }
]
