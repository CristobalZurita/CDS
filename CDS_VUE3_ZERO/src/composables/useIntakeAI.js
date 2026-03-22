import { ref } from 'vue'
import api from '@/services/api'

export function useIntakeAI() {
  const aiLoading = ref(false)
  const aiError = ref('')
  const aiSuggestion = ref(null)

  async function consultarIA(marca, modelo, falla = '') {
    if (!marca?.trim() || !modelo?.trim()) return
    aiLoading.value = true
    aiError.value = ''
    aiSuggestion.value = null
    try {
      const data = await api.post('/chat/intake-assist', { marca, modelo, falla })
      aiSuggestion.value = data
    } catch (e) {
      aiError.value = e?.response?.data?.detail || 'Error al consultar IA'
    } finally {
      aiLoading.value = false
    }
  }

  function clearAI() {
    aiSuggestion.value = null
    aiError.value = ''
  }

  return { aiLoading, aiError, aiSuggestion, consultarIA, clearAI }
}
