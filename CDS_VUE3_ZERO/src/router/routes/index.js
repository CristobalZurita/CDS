import { publicRoutes } from './public'
import { authRoutes } from './auth'
import { clientRoutes } from './client'
import { adminRoutes } from './admin'
import { tokenRoutes } from './token'
import { calculatorRoutes } from './calculators'
import { fallbackRoutes } from './fallback'

export const appRoutes = [
  ...publicRoutes,
  ...authRoutes,
  ...clientRoutes,
  ...adminRoutes,
  ...tokenRoutes,
  ...calculatorRoutes,
  ...fallbackRoutes
]
