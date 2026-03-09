const Timer555Page = () => import('@/pages/calculators/Timer555Page.vue')
const ResistorColorPage = () => import('@/pages/calculators/ResistorColorPage.vue')
const SmdCapacitorPage = () => import('@/pages/calculators/SmdCapacitorPage.vue')
const SmdResistorPage = () => import('@/pages/calculators/SmdResistorPage.vue')
const OhmsLawPage = () => import('@/pages/calculators/OhmsLawPage.vue')
const TemperaturePage = () => import('@/pages/calculators/TemperaturePage.vue')
const NumberSystemPage = () => import('@/pages/calculators/NumberSystemPage.vue')
const LengthPage = () => import('@/pages/calculators/LengthPage.vue')
const AwgPage = () => import('@/pages/calculators/AwgPage.vue')
const VoltageDividerPage = () => import('@/pages/calculators/VoltageDividerPage.vue')
const SeriesParallelResistorPage = () => import('@/pages/calculators/SeriesParallelResistorPage.vue')
const SeriesParallelCapacitorPage = () => import('@/pages/calculators/SeriesParallelCapacitorPage.vue')
const RcTimeConstantPage = () => import('@/pages/calculators/RcTimeConstantPage.vue')
const LowHighPassFilterPage = () => import('@/pages/calculators/LowHighPassFilterPage.vue')
const CurrentDividerPage = () => import('@/pages/calculators/CurrentDividerPage.vue')
const ReactancePage = () => import('@/pages/calculators/ReactancePage.vue')
const LedSeriesResistorPage = () => import('@/pages/calculators/LedSeriesResistorPage.vue')

export const calculatorRoutes = [
  { path: '/calculadoras/timer555', redirect: '/calc/555' },
  { path: '/calculadoras/resistor-color', redirect: '/calc/resistor-color' },
  { path: '/calc/555', name: 'calc-555', component: Timer555Page, meta: { requiresAuth: false } },
  { path: '/calc/resistor-color', name: 'calc-resistor-color', component: ResistorColorPage, meta: { requiresAuth: false } },
  { path: '/calc/smd-capacitor', name: 'calc-smd-capacitor', component: SmdCapacitorPage, meta: { requiresAuth: false } },
  { path: '/calc/smd-resistor', redirect: '/calc/cd40106' },
  { path: '/calc/cd40106', name: 'calc-cd40106', component: SmdResistorPage, meta: { requiresAuth: false } },
  { path: '/calc/ohms-law', name: 'calc-ohms-law', component: OhmsLawPage, meta: { requiresAuth: false } },
  { path: '/calc/temperature', name: 'calc-temperature', component: TemperaturePage, meta: { requiresAuth: false } },
  { path: '/calc/number-system', name: 'calc-number-system', component: NumberSystemPage, meta: { requiresAuth: false } },
  { path: '/calc/length', name: 'calc-length', component: LengthPage, meta: { requiresAuth: false } },
  { path: '/calc/awg', name: 'calc-awg', component: AwgPage, meta: { requiresAuth: false } },
  { path: '/calc/voltage-divider', name: 'calc-voltage-divider', component: VoltageDividerPage, meta: { requiresAuth: false } },
  { path: '/calc/series-parallel-resistor', name: 'calc-series-parallel-resistor', component: SeriesParallelResistorPage, meta: { requiresAuth: false } },
  { path: '/calc/series-parallel-capacitor', name: 'calc-series-parallel-capacitor', component: SeriesParallelCapacitorPage, meta: { requiresAuth: false } },
  { path: '/calc/rc-time-constant', name: 'calc-rc-time-constant', component: RcTimeConstantPage, meta: { requiresAuth: false } },
  { path: '/calc/low-high-pass-filter', name: 'calc-low-high-pass-filter', component: LowHighPassFilterPage, meta: { requiresAuth: false } },
  { path: '/calc/current-divider', name: 'calc-current-divider', component: CurrentDividerPage, meta: { requiresAuth: false } },
  { path: '/calc/reactance', name: 'calc-reactance', component: ReactancePage, meta: { requiresAuth: false } },
  { path: '/calc/led-series-resistor', name: 'calc-led-series-resistor', component: LedSeriesResistorPage, meta: { requiresAuth: false } }
]
