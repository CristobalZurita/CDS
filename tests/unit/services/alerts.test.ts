import { afterEach, describe, expect, it, vi } from 'vitest'

async function loadAlertsModule() {
  vi.resetModules()
  const loggerMock = {
    warn: vi.fn(),
    critical: vi.fn(),
    error: vi.fn(),
  }
  vi.doMock('@/services/logging', () => ({
    logger: loggerMock,
  }))
  const module = await import('@/services/alerts')
  return { ...module, loggerMock }
}

describe('alerts service', () => {
  afterEach(() => {
    vi.resetModules()
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  it('evaluates alert rules from current metrics and live stats', async () => {
    const { AlertService, defaultAlertRules } = await loadAlertsModule()
    const service = new AlertService()

    for (let index = 0; index < 5; index += 1) {
      service.recordMetric('errors', { id: index })
    }

    const errorRateRule = defaultAlertRules.find((rule: any) => rule.id === 'error-rate-high')
    const apiFailureRule = defaultAlertRules.find((rule: any) => rule.id === 'api-failure-rate')
    const criticalRule = defaultAlertRules.find((rule: any) => rule.id === 'critical-error')
    const slowRule = defaultAlertRules.find((rule: any) => rule.id === 'slow-operation')

    service.getMetricsInWindow = vi.fn()
      .mockReturnValueOnce(new Array(5).fill({ timestamp: Date.now() }))
      .mockReturnValueOnce([{ status: 500 }, { status: 200 }]) as any

    expect(service.checkErrorRate(errorRateRule, {})).toBe(true)
    expect(service.checkApiFailureRate(apiFailureRule, {})).toBe(true)
    expect(service.evaluateRule(criticalRule, { criticalCount: 1, slowOperations: [] })).toBe(true)
    expect(service.evaluateRule(slowRule, { criticalCount: 0, slowOperations: [{ duration: 6001 }] })).toBe(true)
  })

  it('fires and resolves alerts while updating metrics and callbacks', async () => {
    const { AlertService, AlertActions, AlertSeverity, AlertRuleTypes, loggerMock } = await loadAlertsModule()
    const service = new AlertService({
      rules: [{
        id: 'slow-rule',
        type: AlertRuleTypes.SLOW_OPERATION,
        enabled: true,
        severity: AlertSeverity.WARNING,
        threshold: 5000,
        windowMs: 60000,
        actions: [AlertActions.LOG],
        description: 'Slow operation detected',
      }],
    })
    const onAlert = vi.fn()
    const onResolve = vi.fn()
    service.on('onAlert', onAlert)
    service.on('onResolve', onResolve)

    const rule = service.rules[0]
    const stats = { errorCount: 1, criticalCount: 0, slowOperations: [{ duration: 7000 }] }

    await service.handleAlert(rule, true, stats)
    expect(service.getMetrics()).toEqual({
      alertsFired: 1,
      alertsResolved: 0,
      activeAlerts: 1,
    })
    expect(service.getActiveAlerts()).toHaveLength(1)
    expect(loggerMock.warn).toHaveBeenCalled()
    expect(onAlert).toHaveBeenCalledWith(rule, stats)

    await service.handleAlert(rule, false, stats)
    expect(service.getMetrics()).toEqual({
      alertsFired: 1,
      alertsResolved: 1,
      activeAlerts: 0,
    })
    expect(service.getActiveAlerts()).toHaveLength(0)
    expect(onResolve).toHaveBeenCalledWith(rule, stats)
  })

  it('executes notification, webhook, slack and email actions with the current adapters', async () => {
    const { AlertService, AlertActions, AlertSeverity, AlertRuleTypes } = await loadAlertsModule()
    const emailService = {
      send: vi.fn().mockResolvedValue(undefined),
    }
    const notificationMock = vi.fn()
    Object.assign(notificationMock, {
      permission: 'granted',
      requestPermission: vi.fn().mockResolvedValue('granted'),
    })
    vi.stubGlobal('Notification', notificationMock)
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true }))

    const service = new AlertService({
      webhookUrl: 'https://hooks.example.com/alert',
      slackWebhook: 'https://hooks.slack.test/alert',
      emailService,
    })

    const rule = {
      id: 'critical-rule',
      type: AlertRuleTypes.CRITICAL_ERROR,
      enabled: true,
      severity: AlertSeverity.CRITICAL,
      threshold: 1,
      windowMs: 0,
      actions: [AlertActions.NOTIFY, AlertActions.WEBHOOK, AlertActions.EMAIL, AlertActions.SLACK],
      description: 'Critical error detected',
    }
    const stats = { errorCount: 3, criticalCount: 1, slowOperations: [] }

    await service.executeActions(rule, 'fire', stats)

    const fetchMock = global.fetch as unknown as ReturnType<typeof vi.fn>
    expect(notificationMock).toHaveBeenCalledWith('Alert', expect.objectContaining({
      body: '[CRITICAL] Critical error detected (fire)',
      requireInteraction: true,
    }))
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(emailService.send).toHaveBeenCalledWith({
      subject: 'Alert: Critical error detected',
      body: '[CRITICAL] Critical error detected (fire)',
      severity: 'critical',
    })
  })

  it('exposes the singleton service and composable helpers', async () => {
    const { getAlertService, useAlerts, AlertActions, AlertSeverity, AlertRuleTypes } = await loadAlertsModule()

    const singleton = getAlertService({
      rules: [{
        id: 'warn-rule',
        type: AlertRuleTypes.SLOW_OPERATION,
        enabled: true,
        severity: AlertSeverity.WARNING,
        threshold: 1000,
        windowMs: 60000,
        actions: [AlertActions.LOG],
        description: 'Warn',
      }],
    })
    const sameSingleton = getAlertService()
    const api = useAlerts()

    expect(sameSingleton).toBe(singleton)
    api.recordMetric('errors', { id: 'e-1' })
    expect(api.service).toBe(singleton)
    expect(api.getMetrics()).toEqual(singleton.getMetrics())
    expect(typeof api.requestPermission).toBe('function')
    expect(typeof api.on).toBe('function')
  })
})
