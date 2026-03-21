import { computed, ref } from 'vue'

const DASHBOARD_SECTIONS = [
  {
    key: 'overview',
    label: 'Resumen',
    icon: 'fa-solid fa-wave-square',
    accent: '#5a995c',
    title: 'Resumen operativo',
    description: 'Vista general de reparaciones, pagos, compras y movimiento reciente.'
  },
  {
    key: 'repairs',
    label: 'OTs',
    icon: 'fa-solid fa-screwdriver-wrench',
    accent: '#ff8a3d',
    title: 'Mis reparaciones',
    description: 'Seguimiento de OTs activas, historial y estado real del trabajo.'
  },
  {
    key: 'payments',
    label: 'Pagos',
    icon: 'fa-solid fa-money-check-dollar',
    accent: '#bb1d1d',
    title: 'Pagos y comprobantes',
    description: 'Solicitudes pendientes, comprobantes y estado de cobros asociados.'
  },
  {
    key: 'purchases',
    label: 'Compras',
    icon: 'fa-solid fa-cart-shopping',
    accent: '#416a9a',
    title: 'Compras y carrito',
    description: 'Carrito actual, solicitudes de tienda y continuidad de compra.'
  },
  {
    key: 'notifications',
    label: 'Avisos',
    icon: 'fa-solid fa-bell',
    accent: '#7a5ef8',
    title: 'Notificaciones',
    description: 'Avisos operativos, alertas y novedades relevantes del sistema.'
  },
  {
    key: 'profile',
    label: 'Perfil',
    icon: 'fa-solid fa-id-card',
    accent: '#4d4a47',
    title: 'Perfil y preferencias',
    description: 'Datos del cliente, preferencias y accesos a seguridad de cuenta.'
  },
  {
    key: 'schedule',
    label: 'Agenda',
    icon: 'fa-solid fa-calendar-check',
    accent: '#e1af1c',
    title: 'Agenda y diagnóstico',
    description: 'Ingreso rápido al flujo de reserva de hora y disponibilidad.'
  },
]

export function useNeoDashboardState() {
  const activeSection = ref('overview')
  const activeRepairFilter = ref('')
  const activePaymentsFilter = ref('pending')
  const activePurchaseFilter = ref('cart')
  const sectionSheetOpen = ref(false)

  const sections = DASHBOARD_SECTIONS

  const activeSectionMeta = computed(() => {
    return sections.find((section) => section.key === activeSection.value) || sections[0]
  })

  function setActiveSection(sectionKey) {
    if (!sections.some((section) => section.key === sectionKey)) return
    activeSection.value = sectionKey
    sectionSheetOpen.value = false
  }

  function setActiveRepairFilter(filterKey) {
    activeRepairFilter.value = String(filterKey || '')
  }

  function setActivePaymentsFilter(filterKey) {
    activePaymentsFilter.value = String(filterKey || 'pending')
  }

  function setActivePurchaseFilter(filterKey) {
    activePurchaseFilter.value = String(filterKey || 'cart')
  }

  function openSectionSheet() {
    sectionSheetOpen.value = true
  }

  function closeSectionSheet() {
    sectionSheetOpen.value = false
  }

  return {
    sections,
    activeSection,
    activeSectionMeta,
    activeRepairFilter,
    activePaymentsFilter,
    activePurchaseFilter,
    sectionSheetOpen,
    setActiveSection,
    setActiveRepairFilter,
    setActivePaymentsFilter,
    setActivePurchaseFilter,
    openSectionSheet,
    closeSectionSheet,
  }
}

export default useNeoDashboardState
