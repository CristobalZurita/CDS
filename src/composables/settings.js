import { ref, computed } from 'vue'

export function useSettings() {
  const loaderEnabled = ref(true)
  const theme = ref('light')
  const locale = ref('es')

  const getLoaderEnabled = () => loaderEnabled.value
  const setLoaderEnabled = (value) => {
    loaderEnabled.value = value
  }

  const setTheme = (value) => {
    theme.value = value
  }

  const setLocale = (value) => {
    locale.value = value
  }

  return {
    loaderEnabled,
    theme,
    locale,
    getLoaderEnabled,
    setLoaderEnabled,
    setTheme,
    setLocale
  }
}
