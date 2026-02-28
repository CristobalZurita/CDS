const rawDisableFlag = String(import.meta.env.VITE_TURNSTILE_DISABLE || '').toLowerCase()

export const TURNSTILE_BYPASS_TOKEN = 'dev-turnstile-bypass'

export const isTurnstileBypassed =
  import.meta.env.DEV || rawDisableFlag === 'true'

