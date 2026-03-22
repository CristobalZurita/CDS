import api from './api.js'

/**
 * Envía un mensaje al chat inteligente web.
 * @param {Array<{role: string, text: string}>} history
 * @param {string} message
 * @returns {Promise<{reply: string, handoff: string|null, handoff_url: string|null}>}
 */
export async function sendMessage(history, message) {
  const res = await api.post('/chat/message', { history, message })
  return res.data
}

/**
 * Envía un email de contacto desde el formulario inline del chat.
 * @param {{name: string, email: string, message: string}} payload
 * @returns {Promise<{ok: boolean}>}
 */
export async function sendChatContact(payload) {
  const res = await api.post('/chat/contact', payload)
  return res.data
}
