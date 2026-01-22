export function createGtmProvider() {
  return {
    name: 'gtm',
    track: (eventName, payload, context) => {
      if (!window.dataLayer) window.dataLayer = []
      window.dataLayer.push({
        event: eventName,
        ...payload,
        ...context
      })
    }
  }
}
