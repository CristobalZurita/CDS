const Timer555Page = () => import('@/pages/calculators/Timer555Page.vue')
const ResistorColorPage = () => import('@/pages/calculators/ResistorColorPage.vue')
const SmdCapacitorPage = () => import('@/pages/calculators/SmdCapacitorPage.vue')
const SmdResistorPage = () => import('@/pages/calculators/SmdResistorPage.vue')
const OhmsLawPage = () => import('@/pages/calculators/OhmsLawPage.vue')
const TemperaturePage = () => import('@/pages/calculators/TemperaturePage.vue')
const NumberSystemPage = () => import('@/pages/calculators/NumberSystemPage.vue')
const LengthPage = () => import('@/pages/calculators/LengthPage.vue')
const AwgPage = () => import('@/pages/calculators/AwgPage.vue')

export const calculatorRoutes = [
  { path: '/calculadoras/timer555', redirect: '/calc/555' },
  { path: '/calculadoras/resistor-color', redirect: '/calc/resistor-color' },
  { path: '/calc/555', name: 'calc-555', component: Timer555Page, meta: { requiresAuth: false } },
  { path: '/calc/resistor-color', name: 'calc-resistor-color', component: ResistorColorPage, meta: { requiresAuth: false } },
  { path: '/calc/smd-capacitor', name: 'calc-smd-capacitor', component: SmdCapacitorPage, meta: { requiresAuth: false } },
  { path: '/calc/smd-resistor', name: 'calc-smd-resistor', component: SmdResistorPage, meta: { requiresAuth: false } },
  { path: '/calc/ohms-law', name: 'calc-ohms-law', component: OhmsLawPage, meta: { requiresAuth: false } },
  { path: '/calc/temperature', name: 'calc-temperature', component: TemperaturePage, meta: { requiresAuth: false } },
  { path: '/calc/number-system', name: 'calc-number-system', component: NumberSystemPage, meta: { requiresAuth: false } },
  { path: '/calc/length', name: 'calc-length', component: LengthPage, meta: { requiresAuth: false } },
  { path: '/calc/awg', name: 'calc-awg', component: AwgPage, meta: { requiresAuth: false } }
]
