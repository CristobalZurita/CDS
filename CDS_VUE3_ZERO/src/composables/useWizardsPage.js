import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { extractErrorMessage } from '@/services/api'
import {
  cancelRepairSignatureRequest,
  requestRepairPhotoUploadLink,
  requestRepairSignatureLink
} from '@/services/repairDetailAdminService'

const WIZARD_CARDS = [
  {
    id: 'intake',
    title: 'Cliente + Instrumento + OT',
    description: 'Flujo completo de ingreso: crea cliente, equipo y OT en un solo paso.',
    routeName: 'admin-intake',
    cta: 'Nuevo Ingreso'
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
  const signatureRequest = ref(null)
  const photoRequest = ref(null)

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
    signatureRequest.value = null

    const repairId = Number(signatureForm.value.repair_id || 0)
    if (!repairId) {
      error.value = 'Debes ingresar un ID de reparacion valido.'
      return
    }

    loading.value = true

    try {
      const nextRequest = await requestRepairSignatureLink(
        repairId,
        String(signatureForm.value.request_type || 'ingreso'),
        { expiresMinutes: Number(signatureForm.value.expires_minutes || 5) }
      )

      signatureRequest.value = nextRequest || null
      if (nextRequest?.url) {
        signatureLink.value = nextRequest.url
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
    photoRequest.value = null

    const repairId = Number(photoRequestForm.value.repair_id || 0)
    if (!repairId) {
      error.value = 'Debes ingresar un ID de reparacion valido.'
      return
    }

    loading.value = true

    try {
      const nextRequest = await requestRepairPhotoUploadLink(repairId, {
        photoType: String(photoRequestForm.value.photo_type || 'client'),
        expiresMinutes: Number(photoRequestForm.value.expires_minutes || 10)
      })
      photoRequest.value = nextRequest || null
      if (nextRequest?.url) {
        photoLink.value = nextRequest.url
        success.value = 'Link de carga de foto generado correctamente.'
      }
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function cancelSignatureLink() {
    const requestId = Number(signatureRequest.value?.id || 0)
    if (!requestId) return

    clearFeedback()
    loading.value = true

    try {
      await cancelRepairSignatureRequest(requestId)
      signatureRequest.value = signatureRequest.value
        ? { ...signatureRequest.value, status: 'cancelled', url: '' }
        : null
      signatureLink.value = ''
      success.value = 'Solicitud de firma cancelada.'
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
    signatureRequest,
    photoRequest,
    openWizard,
    clearFeedback,
    requestSignatureLink,
    requestPhotoLink,
    cancelSignatureLink
  }
}
