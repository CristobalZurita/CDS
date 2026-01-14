import { createRouter, createWebHistory } from 'vue-router';

export const routes = [
  { path: '/', component: () => import('@/views/HomeView.vue') },
  { path: '/calc/555', component: () => import('@/modules/timer555/Timer555View.vue') },
  { path: '/calc/resistor-color', component: () => import('@/modules/resistorColor/ResistorColorView.vue') },
  { path: '/calc/smd-capacitor', component: () => import('@/modules/smdCapacitor/SmdCapacitorView.vue') },
  { path: '/calc/smd-resistor', component: () => import('@/modules/smdResistor/SmdResistorView.vue') },
  { path: '/calc/ohms-law', component: () => import('@/modules/ohmsLaw/OhmsLawView.vue') },
  { path: '/calc/temperature', component: () => import('@/modules/temperature/TemperatureView.vue') },
  { path: '/calc/number-system', component: () => import('@/modules/numberSystem/NumberSystemView.vue') },
  { path: '/calc/length', component: () => import('@/modules/length/LengthView.vue') },
  { path: '/calc/awg', component: () => import('@/modules/awg/AwgView.vue') }
];

export default createRouter({
  history: createWebHistory(),
  routes
});
