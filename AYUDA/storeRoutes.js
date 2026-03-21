/**
 * router/routes/public.js  — VERSIÓN ACTUALIZADA
 * Agrega las rutas de tienda al archivo existente.
 * Fusionar con tu public.js actual.
 */

// ── Rutas a AGREGAR en tu public.js existente ─────────────

export const storeRoutes = [
  {
    path:      '/tienda',
    name:      'store',
    component: () => import('@/pages/public/StorePage.vue'),
    meta:      { title: 'Tienda — CDS' },
  },
  {
    path:      '/tienda/checkout',
    name:      'store-checkout',
    component: () => import('@/pages/public/CheckoutPage.vue'),
    meta:      { title: 'Checkout — CDS' },
  },
  {
    path:      '/tienda/pago/resultado',
    name:      'store-payment-result',
    component: () => import('@/pages/public/PaymentResultPage.vue'),
    meta:      { title: 'Resultado de pago — CDS' },
  },
]

/*
  En tu router/routes/public.js actual, importar y spread:

  import { storeRoutes } from './storeRoutes.js'

  export default [
    { path: '/', ... },          // rutas existentes
    ...storeRoutes,              // agregar aquí
  ]
*/
