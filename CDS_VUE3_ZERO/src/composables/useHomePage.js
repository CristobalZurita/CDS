import { computed } from 'vue'

export function useHomePage() {
  const heroTitle = computed(() => 'Cirujano de Sintetizadores')
  const heroSubtitle = computed(() => 'Reparación, diagnóstico y soporte para instrumentos electrónicos.')

  const primaryActions = computed(() => ([
    { label: 'Agendar revisión', to: '/agendar', variant: 'primary' },
    { label: 'Cotizar', to: '/cotizador', variant: 'secondary' }
  ]))

  const sections = computed(() => ([
    { id: 'hero', name: 'Inicio', icon: '' },
    { id: 'about', name: 'Nosotros', icon: 'pi pi-box' },
    { id: 'services', name: 'Servicios', icon: 'pi pi-wrench' },
    { id: 'featured', name: 'Trabajos', icon: 'pi pi-qrcode' },
    { id: 'faq', name: 'Preguntas', icon: 'pi pi-question-circle' },
    { id: 'reviews', name: 'Opiniones', icon: 'fa-regular fa-comment' },
    { id: 'contact', name: 'Contacto', icon: 'fa-regular fa-envelope' }
  ]))

  const contentSections = computed(() => ([
    {
      id: 'about',
      title: 'Nosotros',
      description: 'Espacio de presentación del taller y su enfoque de reparación.',
      links: [{ label: 'Ver términos', to: '/terminos' }]
    },
    {
      id: 'services',
      title: 'Servicios',
      description: 'Resumen de servicios disponibles para diagnóstico, reparación y seguimiento.',
      links: [
        { label: 'Agendar', to: '/agendar' },
        { label: 'Calculadoras', to: '/calculadoras' }
      ]
    },
    {
      id: 'diagnostic',
      title: 'Cotizar',
      description: 'Acceso a estimación inicial y flujo de evaluación técnica.',
      links: [{ label: 'Ir al cotizador', to: '/cotizador' }]
    },
    {
      id: 'featured',
      title: 'Trabajos',
      description: 'Vitrina de resultados y recursos públicos del sitio.',
      links: [{ label: 'Ir a tienda', to: '/tienda' }]
    },
    {
      id: 'faq',
      title: 'Preguntas',
      description: 'Referencia rápida a políticas y términos vigentes.',
      links: [
        { label: 'Política de privacidad', to: '/privacidad' },
        { label: 'Términos y condiciones', to: '/terminos' }
      ]
    },
    {
      id: 'reviews',
      title: 'Opiniones',
      description: 'Sección de validación social y experiencia de clientes.',
      links: [{ label: 'Volver arriba', to: '/' }]
    },
    {
      id: 'contact',
      title: 'Contacto',
      description: 'Canales de contacto y coordinación de atención.',
      links: [{ label: 'Solicitar agenda', to: '/agendar' }]
    }
  ]))

  return {
    heroTitle,
    heroSubtitle,
    primaryActions,
    sections,
    contentSections
  }
}
