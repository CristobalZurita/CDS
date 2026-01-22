export function createConsoleProvider() {
  return {
    name: 'console',
    track: (eventName, payload, context) => {
      // eslint-disable-next-line no-console
      console.log('[analytics]', eventName, { payload, context })
    }
  }
}
