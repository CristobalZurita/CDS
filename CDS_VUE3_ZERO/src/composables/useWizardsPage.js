import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { extractErrorMessage } from '@new/services/api'

const WIZARD_CARDS = [
  {
    id: 'intake',
    title: 'Cliente + Instrumento + OT',
    description: 'Acceso directo al flujo de intake y creacion de OT.',
    routeName: 'admin-clients',
    cta: 'Ir a Clientes'
  },
  {
    id: 'inventory',
    title: 'Inventario',
    description: 'Alta y control de items de inventario.',
    routeName: 'admin-inventory',
    cta: 'Ir a Inventario'
  },
  {
    id: 'tickets',
    title: 'Tickets',
    description: 'Crear y gestionar tickets internos del taller.',
    routeName: 'admin-tickets',
    cta: 'Ir a Tickets'
  },
  {
    id: 'purchase',
    title: 'Compras sugeridas',
    description: 'Solicitudes de compra y estados de pago.',
    routeName: 'admin-purchase-requests',
    cta: 'Ir a Compras'
  },
  {
    id: 'manuals',
    title: 'Manuales',
    description: 'Documentos tecnicos por instrumento y modelo.',
    routeName: 'admin-manuals',
    cta: 'Ir a Manuales'
  },
  {
    id: 'repairs',
    title: 'Reparaciones',
    description: 'Seguimiento de OT activas y detalle tecnico.',
    routeName: 'admin-repairs',
    cta: 'Ir a Reparaciones'
  }
]

export function useWizardsPage() {
  const router = useRouter()

  const cards = ref(WIZARD_CARDS)
  const loading = ref(false)
  const error = ref('')
  const success = ref('')

  const signatureForm = ref({
    repair_id: '',
    request_type: 'ingreso',
    expires_minutes: 5
  })

  const photoRequestForm = ref({
    repair_id: '',
    photo_type: 'client',
    expires_minutes: 10
  })

  const signatureLink = ref('')
  const photoLink = ref('')

  function clearFeedback() {
    error.value = ''
    success.value = ''
  }

  function openWizard(card) {
    if (!card?.routeName) return
    router.push({ name: card.routeName })
  }

  async function requestSignatureLink() {
    clearFeedback()
    signatureLink.value = ''

    const repairId = Number(signatureForm.value.repair_id || 0)
    if (!repairId) {
      error.value = 'Debes ingresar un ID de reparacion valido.'
      return
    }

    loading.value = true

    try {
      const response = await api.post('/signatures/requests', {
        repair_id: repairId,
        request_type: String(signatureForm.value.request_type || 'ingreso'),
        expires_minutes: Number(signatureForm.value.expires_minutes || 5)
      })

      const token = response?.data?.token || response?.token || ''
      if (token) {
        signatureLink.value = `${window.location.origin}/signature/${token}`
        success.value = 'Link de firma generado correctamente.'
      }
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function requestPhotoLink() {
    clearFeedback()
    photoLink.value = ''

    const repairId = Number(photoRequestForm.value.repair_id || 0)
    if (!repairId) {
      error.value = 'Debes ingresar un ID de reparacion valido.'
      return
    }

    loading.value = true

    try {
      const response = await api.post('/photo-requests/', null, {
        params: {
          repair_id: repairId,
          photo_type: String(photoRequestForm.value.photo_type || 'client'),
          expires_minutes: Number(photoRequestForm.value.expires_minutes || 10)
        }
      })

      const token = response?.data?.token || response?.token || ''
      if (token) {
        photoLink.value = `${window.location.origin}/photo-upload/${token}`
        success.value = 'Link de carga de foto generado correctamente.'
      }
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  return {
    cards,
    loading,
    error,
    success,
    signatureForm,
    photoRequestForm,
    signatureLink,
    photoLink,
    openWizard,
    clearFeedback,
    requestSignatureLink,
    requestPhotoLink
  }
}
