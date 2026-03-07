import { computed } from 'vue'

export function useLicensePage() {
  const title = computed(() => 'Términos y Condiciones')
  const subtitle = computed(() => 'Licencia de uso y atribuciones')

  const sections = computed(() => ([
    {
      id: 'intro',
      title: '',
      items: [
        'Este sitio web fue desarrollado utilizando tecnologías de código abierto. El template base está licenciado bajo la licencia MIT, lo que permite su uso, modificación y distribución siempre que se incluya el aviso de copyright correspondiente.'
      ]
    },
    {
      id: 'uso',
      title: 'Uso del sitio',
      items: [
        'Este sitio web es propiedad de Cirujano de Sintetizadores y tiene como objetivo informar sobre los servicios de reparación, restauración y modificación de equipos de audio electrónico.',
        'El contenido de este sitio, incluyendo textos, imágenes y diseño, está protegido por derechos de autor. No está permitida su reproducción sin autorización previa.'
      ]
    },
    {
      id: 'servicios',
      title: 'Servicios',
      items: [
        'Los servicios ofrecidos por Cirujano de Sintetizadores incluyen diagnóstico, reparación, restauración, modificación y mantenimiento de sintetizadores, teclados, drum machines y otros equipos de audio profesional.',
        'Cada trabajo se realiza bajo presupuesto previo aprobado por el cliente. Los plazos de entrega y garantías se especifican en cada cotización según el tipo de trabajo a realizar.'
      ]
    },
    {
      id: 'responsabilidad',
      title: 'Responsabilidad',
      items: [
        'Cirujano de Sintetizadores no se hace responsable por equipos abandonados después de 90 días de notificada la finalización del trabajo o el presupuesto rechazado.',
        'El cliente es responsable del embalaje adecuado para envíos. Los costos de envío corren por cuenta del cliente tanto para la entrega como para la devolución del equipo.'
      ]
    },
    {
      id: 'contacto',
      title: 'Contacto',
      items: [
        'Para consultas sobre estos términos y condiciones, puedes contactarnos a través del formulario de contacto en este sitio o mediante nuestras redes sociales oficiales.'
      ]
    }
  ]))

  return {
    title,
    subtitle,
    sections
  }
}
