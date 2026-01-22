import { createConsoleProvider } from './providers/consoleProvider'
import { createGtmProvider } from './providers/gtmProvider'

const defaultContext = {
  app: 'cirujano-front',
  env: import.meta.env.MODE
}

let providers = []
let analyticsMode = import.meta.env.VITE_ANALYTICS_MODE || 'dev'

export function initAnalytics(mode = analyticsMode) {
  analyticsMode = mode
  providers = []

  if (analyticsMode === 'dev') {
    providers.push(createConsoleProvider())
    return
  }

  if (analyticsMode === 'prod') {
    providers.push(createGtmProvider())
  }
}

export function track(eventName, payload = {}, context = {}) {
  if (analyticsMode === 'off') return
  const mergedContext = { ...defaultContext, ...context }
  providers.forEach((provider) => provider.track(eventName, payload, mergedContext))
}

export function setAnalyticsContext(ctx = {}) {
  Object.assign(defaultContext, ctx)
}
