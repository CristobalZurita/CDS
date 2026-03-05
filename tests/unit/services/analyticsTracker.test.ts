import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

async function loadTracker() {
  vi.resetModules()
  return import('@/analytics/tracker')
}

describe('analytics tracker', () => {
  beforeEach(() => {
    delete (window as any).dataLayer
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('tracks through console provider in dev mode', async () => {
    const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    const tracker = await loadTracker()

    tracker.initAnalytics('dev')
    tracker.track('diagnostic_opened', { source: 'wizard' }, { userId: 'u-1' })

    expect(logSpy).toHaveBeenCalledWith(
      '[analytics]',
      'diagnostic_opened',
      expect.objectContaining({
        payload: { source: 'wizard' },
        context: expect.objectContaining({
          app: 'cirujano-front',
          userId: 'u-1',
        }),
      })
    )
  })

  it('tracks through GTM provider in prod mode', async () => {
    const tracker = await loadTracker()

    tracker.initAnalytics('prod')
    tracker.track('checkout_started', { cartSize: 2 }, { sessionId: 's-1' })

    expect((window as any).dataLayer).toBeDefined()
    expect((window as any).dataLayer).toHaveLength(1)
    expect((window as any).dataLayer[0]).toMatchObject({
      event: 'checkout_started',
      cartSize: 2,
      sessionId: 's-1',
      app: 'cirujano-front',
    })
  })

  it('supports custom context and disables tracking in off mode', async () => {
    const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    const tracker = await loadTracker()

    tracker.initAnalytics('dev')
    tracker.setAnalyticsContext({ workspace: 'cds' })
    tracker.track('context_event')

    expect(logSpy).toHaveBeenCalledWith(
      '[analytics]',
      'context_event',
      expect.objectContaining({
        context: expect.objectContaining({ workspace: 'cds' }),
      })
    )

    logSpy.mockClear()
    tracker.initAnalytics('off')
    tracker.track('disabled_event', { x: 1 }, { y: 2 })
    expect(logSpy).not.toHaveBeenCalled()
  })
})
