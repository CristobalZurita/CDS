<template>
  <div class="turnstile-widget">
    <div
      v-if="isTurnstileBypassed"
      class="turnstile-bypass"
      data-testid="turnstile-bypass"
    >
      Captcha desactivado para pruebas
    </div>
    <div ref="containerRef"></div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const emit = defineEmits(['verify'])
const containerRef = ref(null)
let widgetId = null

const siteKey = import.meta.env.VITE_TURNSTILE_SITE_KEY
const rawDisableFlag = String(import.meta.env.VITE_TURNSTILE_DISABLE || '').toLowerCase()
const isTurnstileBypassed = rawDisableFlag === 'true'
const turnstileBypassToken = 'dev-turnstile-bypass'

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
  if (!siteKey || !containerRef.value || !window.turnstile) {
    if (!siteKey) {
      console.warn('[turnstile] Missing VITE_TURNSTILE_SITE_KEY')
    }
    return
  }
  widgetId = window.turnstile.render(containerRef.value, {
    sitekey: siteKey,
    callback: (token) => emit('verify', token),
    'error-callback': () => {
      console.warn('[turnstile] Error callback fired')
      emit('verify', '')
    },
    'expired-callback': () => emit('verify', '')
  })
}

onMounted(async () => {
  if (isTurnstileBypassed) {
    emit('verify', turnstileBypassToken)
    return
  }

  try {
    await loadScript()
    renderWidget()
  } catch (error) {
    console.warn('[turnstile] Failed to initialize widget', error)
    emit('verify', '')
  }
})
</script>

<style scoped>
.turnstile-widget {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  margin: 1rem 0;
}

.turnstile-bypass {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.6rem 0.9rem;
  border-radius: 999px;
  /* VERDE ELIMINADO: Reemplazado por naranja/primary */
  background: rgba(236, 107, 0, 0.12); /* rgba($color-primary, 0.12) */
  border: 1px solid rgba(236, 107, 0, 0.35); /* rgba($color-primary, 0.35) */
  color: #b34f00; /* darken($color-primary, 15%) */
  font-size: 1rem; /* AUMENTADO de 0.9rem a 1rem para mejor legibilidad */
  font-weight: 600;
}
</style>
