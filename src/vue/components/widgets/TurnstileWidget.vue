<template>
  <div class="turnstile-widget">
    <div ref="containerRef"></div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const emit = defineEmits(['verify'])
const containerRef = ref(null)
let widgetId = null

const siteKey = import.meta.env.VITE_TURNSTILE_SITE_KEY

const loadScript = () => {
  return new Promise((resolve, reject) => {
    if (window.turnstile) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit'
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Turnstile script failed'))
    document.head.appendChild(script)
  })
}

const renderWidget = () => {
  if (!siteKey || !containerRef.value || !window.turnstile) return
  widgetId = window.turnstile.render(containerRef.value, {
    sitekey: siteKey,
    callback: (token) => emit('verify', token),
    'error-callback': () => emit('verify', ''),
    'expired-callback': () => emit('verify', '')
  })
}

onMounted(async () => {
  await loadScript()
  renderWidget()
})
</script>

<style scoped>
.turnstile-widget {
  display: flex;
  justify-content: center;
  margin: 1rem 0;
}
</style>
