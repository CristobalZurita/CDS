const Timer555Page = () => import('@new/pages/calculators/Timer555Page.vue')
const ResistorColorPage = () => import('@new/pages/calculators/ResistorColorPage.vue')
const SmdCapacitorPage = () => import('@new/pages/calculators/SmdCapacitorPage.vue')
const SmdResistorPage = () => import('@new/pages/calculators/SmdResistorPage.vue')
const OhmsLawPage = () => import('@new/pages/calculators/OhmsLawPage.vue')
const TemperaturePage = () => import('@new/pages/calculators/TemperaturePage.vue')
const NumberSystemPage = () => import('@new/pages/calculators/NumberSystemPage.vue')
const LengthPage = () => import('@new/pages/calculators/LengthPage.vue')
const AwgPage = () => import('@new/pages/calculators/AwgPage.vue')

export const calculatorRoutes = [
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
