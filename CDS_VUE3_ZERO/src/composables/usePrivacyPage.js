import { computed } from 'vue'

export function usePrivacyPage() {
  const backToTerms = computed(() => '/terminos')
  const backToHome = computed(() => '/')

  return {
    backToTerms,
    backToHome
  }
}
