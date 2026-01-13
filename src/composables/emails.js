import { ref } from 'vue'

export function useEmails() {
  const emails = ref([])

  const init = () => {
    // Initialize email service
  }

  const send = async (email) => {
    // Send email
    return true
  }

  return {
    emails,
    init,
    send
  }
}
