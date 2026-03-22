import { ref } from 'vue'
import { sendMessage, sendChatContact } from '@/services/chatService'

export function useChatWidget() {
  const open = ref(false)
  const loading = ref(false)
  const messages = ref([]) // [{ role: 'user'|'model', text: '' }]
  const handoff = ref(null) // 'whatsapp' | 'email' | null
  const handoffUrl = ref(null)
  const input = ref('')
  const error = ref('')

  // Estado del formulario inline de email
  const emailForm = ref({ name: '', email: '', message: '' })
  const sendingEmail = ref(false)
  const emailError = ref('')

  function toggle() {
    open.value = !open.value
  }

  async function send() {
    const text = input.value.trim()
    if (!text || loading.value) return

    messages.value.push({ role: 'user', text })
    input.value = ''
    handoff.value = null
    handoffUrl.value = null
    error.value = ''
    loading.value = true

    try {
      const history = messages.value.slice(0, -1)
      const res = await sendMessage(history, text)
      messages.value.push({ role: 'model', text: res.reply })
      if (res.handoff) {
        handoff.value = res.handoff
        handoffUrl.value = res.handoff_url || null
      }
    } catch {
      error.value = 'Hubo un problema al conectar. Intenta de nuevo.'
      messages.value.pop()
    } finally {
      loading.value = false
    }
  }

  async function submitEmailForm() {
    emailError.value = ''
    const { name, email, message } = emailForm.value
    if (!name.trim() || !email.trim() || !message.trim()) {
      emailError.value = 'Completa todos los campos.'
      return
    }
    sendingEmail.value = true
    try {
      await sendChatContact({ name: name.trim(), email: email.trim(), message: message.trim() })
      messages.value.push({ role: 'model', text: '¡Mensaje enviado! Cristobal te responderá a la brevedad.' })
      handoff.value = null
      handoffUrl.value = null
      emailForm.value = { name: '', email: '', message: '' }
      // Cerrar el panel después de 2.5 segundos
      setTimeout(() => { open.value = false }, 2500)
    } catch {
      emailError.value = 'No se pudo enviar. Intenta de nuevo.'
    } finally {
      sendingEmail.value = false
    }
  }

  function confirmHandoff() {
    messages.value.push({
      role: 'model',
      text: 'Listo. Te abrí WhatsApp en una nueva pestaña. Si necesitas algo más, estoy aquí.',
    })
    handoff.value = null
    handoffUrl.value = null
  }

  function clear() {
    messages.value = []
    handoff.value = null
    handoffUrl.value = null
    input.value = ''
    error.value = ''
    emailForm.value = { name: '', email: '', message: '' }
    emailError.value = ''
  }

  return {
    open,
    loading,
    messages,
    handoff,
    handoffUrl,
    input,
    error,
    emailForm,
    sendingEmail,
    emailError,
    toggle,
    send,
    submitEmailForm,
    confirmHandoff,
    clear,
  }
}
