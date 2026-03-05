import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { LogLevel, logger, useLogging } from '@/services/logging'

describe('logging service', () => {
  beforeEach(() => {
    logger.clearLogs()
    logger.clearMetrics()
    localStorage.clear()
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true }))
    vi.spyOn(console, 'log').mockImplementation(() => undefined)
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
  })

  afterEach(() => {
    logger.clearLogs()
    logger.clearMetrics()
    localStorage.clear()
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('stores, filters and exports logs', () => {
    const warnSpy = vi.spyOn(logger, 'warn')

    logger.info('App ready', { page: 'home' })
    logger.trackMetric('slow-navigation', 1501, { route: '/dashboard' })

    const infoLogs = logger.getLogs(LogLevel.INFO)
    const allLogs = logger.getLogs()

    expect(infoLogs).toHaveLength(1)
    expect(infoLogs[0].message).toBe('App ready')
    expect(allLogs.some((entry) => entry.message.includes('Slow operation: slow-navigation'))).toBe(true)
    expect(warnSpy).toHaveBeenCalled()
    expect(logger.exportLogs('json')).toContain('"App ready"')
    expect(logger.exportLogs('csv')).toContain('"timestamp","level","message","context"')
  })

  it('tracks metrics for successful and failing async measurements', async () => {
    await expect(logger.measure('sync-catalog', async () => 'ok', { mode: 'full' })).resolves.toBe('ok')
    await expect(logger.measure('broken-task', async () => {
      throw new Error('broken')
    }, { scope: 'unit' })).rejects.toThrow('broken')

    const metrics = logger.getMetrics()

    expect(metrics).toHaveLength(2)
    expect(metrics[0].name).toBe('sync-catalog')
    expect(metrics[0].metadata).toEqual({ mode: 'full' })
    expect(metrics[1].name).toBe('broken-task')
    expect(String(metrics[1].metadata?.error)).toContain('Error: broken')
  })

  it('sends error-level logs to the backend transport', () => {
    const fetchMock = global.fetch as unknown as ReturnType<typeof vi.fn>

    logger.error('Backend failed', { status: 500 }, 'stacktrace')
    logger.critical('System unavailable', { scope: 'payments' })

    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      '/api/logs',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
    )
    expect(logger.getLogs(LogLevel.ERROR)).toHaveLength(1)
    expect(logger.getLogs(LogLevel.CRITICAL)).toHaveLength(1)
  })

  it('exposes bound helper methods through useLogging', () => {
    const api = useLogging()

    api.trackApiCall('GET', '/health', 123, 200)
    api.trackUserAction('click', 'quote-button', { section: 'hero' })
    api.trackError(new Error('Boom'), { scope: 'unit' })

    expect(api.logger).toBe(logger)
    expect(logger.getMetrics('API GET /health')).toHaveLength(1)
    expect(logger.getLogs().some((entry) => entry.message === 'User action: click')).toBe(true)
    expect(logger.getLogs().some((entry) => entry.message === 'Boom')).toBe(true)
  })
})
