import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

export function useTermsPage() {
  const router = useRouter()
  const accepted = ref(false)

  const canContinue = computed(() => accepted.value)

  function goToPrivacy() {
    if (!canContinue.value) return
    router.push('/privacidad')
  }

  return {
    accepted,
    canContinue,
    goToPrivacy
  }
}
