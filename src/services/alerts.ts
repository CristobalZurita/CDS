import { logger } from '@/services/logging'

/**
 * Alert Rule Types
 */
export const AlertRuleTypes = {
    ERROR_RATE: 'error_rate',           // Errors per minute exceed threshold
    CRITICAL_ERROR: 'critical_error',   // Critical errors detected
    SLOW_OPERATION: 'slow_operation',   // Operation takes longer than threshold
    API_FAILURE: 'api_failure',         // API call failure rate exceeds threshold
    MEMORY_USAGE: 'memory_usage',       // Memory usage exceeds threshold
    DISK_USAGE: 'disk_usage'            // Disk usage exceeds threshold
}

/**
 * Alert Severity Levels
 */
export const AlertSeverity = {
    INFO: 'info',
    WARNING: 'warning',
    ERROR: 'error',
    CRITICAL: 'critical'
}

/**
 * Alert Actions (what to do when triggered)
 */
export const AlertActions = {
    LOG: 'log',
    NOTIFY: 'notify',
    WEBHOOK: 'webhook',
    EMAIL: 'email',
    SLACK: 'slack'
}

/**
 * Default Alert Rules Configuration
 */
export const defaultAlertRules = [
    {
        id: 'error-rate-high',
        type: AlertRuleTypes.ERROR_RATE,
        enabled: true,
        severity: AlertSeverity.WARNING,
        threshold: 5,                    // 5 errors per minute
        windowMs: 60000,                 // 1 minute window
        actions: [AlertActions.LOG, AlertActions.NOTIFY],
        description: 'Triggered when error rate exceeds 5/minute'
    },
    {
        id: 'critical-error',
        type: AlertRuleTypes.CRITICAL_ERROR,
        enabled: true,
        severity: AlertSeverity.CRITICAL,
        threshold: 1,                    // Any critical error
        windowMs: 0,                     // Immediate
        actions: [AlertActions.LOG, AlertActions.NOTIFY, AlertActions.SLACK],
        description: 'Triggered immediately on any critical error'
    },
    {
        id: 'slow-operation',
        type: AlertRuleTypes.SLOW_OPERATION,
        enabled: true,
        severity: AlertSeverity.WARNING,
        threshold: 5000,                 // 5 seconds
        windowMs: 300000,                // 5 minute window
        actions: [AlertActions.LOG],
        description: 'Triggered when operation takes longer than 5s'
    },
    {
        id: 'api-failure-rate',
        type: AlertRuleTypes.API_FAILURE,
        enabled: true,
        severity: AlertSeverity.ERROR,
        threshold: 0.1,                  // 10% failure rate
        windowMs: 300000,                // 5 minute window
        actions: [AlertActions.LOG, AlertActions.NOTIFY],
        description: 'Triggered when API failure rate exceeds 10%'
    }
]

/**
 * Alert History - for tracking active alerts
 */
const alertHistory = new Map()

/**
 * Alert Notification Handler
 */
export class AlertService {
    constructor(options = {}) {
        this.rules = options.rules || defaultAlertRules
        this.webhookUrl = options.webhookUrl || null
        this.slackWebhook = options.slackWebhook || null
        this.emailService = options.emailService || null
        this.callbacks = new Map()
        this.metrics = {
            alertsFired: 0,
            alertsResolved: 0,
            activeAlerts: 0
        }
    }

    /**
     * Check alert conditions and fire if needed
     */
    async checkAlerts(stats) {
        for (const rule of this.rules.filter(r => r.enabled)) {
            const shouldFire = this.evaluateRule(rule, stats)
            await this.handleAlert(rule, shouldFire, stats)
        }
    }

    /**
     * Evaluate if alert rule should be triggered
     */
    evaluateRule(rule, stats) {
        switch (rule.type) {
            case AlertRuleTypes.ERROR_RATE:
                return this.checkErrorRate(rule, stats)
            
            case AlertRuleTypes.CRITICAL_ERROR:
                return stats.criticalCount > 0
            
            case AlertRuleTypes.SLOW_OPERATION:
                return stats.slowOperations.some(op => op.duration > rule.threshold)
            
            case AlertRuleTypes.API_FAILURE:
                return this.checkApiFailureRate(rule, stats)
            
            default:
                return false
        }
    }

    /**
     * Check error rate
     */
    checkErrorRate(rule, stats) {
        const lastErrors = this.getMetricsInWindow(rule.windowMs, 'errors') || []
        return lastErrors.length >= rule.threshold
    }

    /**
     * Check API failure rate
     */
    checkApiFailureRate(rule, stats) {
        const recentCalls = this.getMetricsInWindow(rule.windowMs, 'api_calls') || []
        if (recentCalls.length === 0) return false
        
        const failures = recentCalls.filter(c => c.status >= 400).length
        const failureRate = failures / recentCalls.length
        return failureRate > rule.threshold
    }

    /**
     * Get metrics within time window
     */
    getMetricsInWindow(windowMs, type) {
        if (windowMs === 0) return [] // Immediate alerts
        const now = Date.now()
        const key = `${type}_history`
        
        if (!alertHistory.has(key)) {
            alertHistory.set(key, [])
        }
        
        const history = alertHistory.get(key)
        return history.filter(item => now - item.timestamp < windowMs)
    }

    /**
     * Record metric for alert evaluation
     */
    recordMetric(type, data) {
        const key = `${type}_history`
        if (!alertHistory.has(key)) {
            alertHistory.set(key, [])
        }
        
        const history = alertHistory.get(key)
        history.push({
            timestamp: Date.now(),
            data
        })
        
        // Keep only recent data (last hour)
        if (history.length > 1000) {
            history.shift()
        }
    }

    /**
     * Handle alert trigger or resolution
     */
    async handleAlert(rule, shouldFire, stats) {
        const ruleKey = rule.id
        const isActive = alertHistory.has(`alert_${ruleKey}`)

        if (shouldFire && !isActive) {
            // Alert triggered
            alertHistory.set(`alert_${ruleKey}`, {
                firedAt: Date.now(),
                rule
            })
            this.metrics.alertsFired++
            this.metrics.activeAlerts++

            await this.executeActions(rule, 'fire', stats)
            
            if (this.callbacks.has('onAlert')) {
                this.callbacks.get('onAlert')(rule, stats)
            }

        } else if (!shouldFire && isActive) {
            // Alert resolved
            alertHistory.delete(`alert_${ruleKey}`)
            this.metrics.alertsResolved++
            this.metrics.activeAlerts--

            await this.executeActions(rule, 'resolve', stats)
            
            if (this.callbacks.has('onResolve')) {
                this.callbacks.get('onResolve')(rule, stats)
            }
        }
    }

    /**
     * Execute alert actions
     */
    async executeActions(rule, action, stats) {
        const message = `[${rule.severity.toUpperCase()}] ${rule.description} (${action})`
        
        for (const actionType of rule.actions) {
            switch (actionType) {
                case AlertActions.LOG:
                    logger[rule.severity === AlertSeverity.CRITICAL ? 'critical' : 'warn'](
                        message,
                        { rule: rule.id, stats }
                    )
                    break

                case AlertActions.NOTIFY:
                    this.sendNotification(message, rule.severity)
                    break

                case AlertActions.WEBHOOK:
                    if (this.webhookUrl) {
                        await this.sendWebhook(message, rule, stats)
                    }
                    break

                case AlertActions.EMAIL:
                    if (this.emailService) {
                        await this.emailService.send({
                            subject: `Alert: ${rule.description}`,
                            body: message,
                            severity: rule.severity
                        })
                    }
                    break

                case AlertActions.SLACK:
                    if (this.slackWebhook) {
                        await this.sendSlack(message, rule, stats)
                    }
                    break
            }
        }
    }

    /**
     * Send browser notification
     */
    sendNotification(message, severity) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Alert', {
                body: message,
                icon: this.getIconForSeverity(severity),
                tag: 'alert',
                requireInteraction: severity === AlertSeverity.CRITICAL
            })
        }
    }

    /**
     * Send webhook notification
     */
    async sendWebhook(message, rule, stats) {
        try {
            await fetch(this.webhookUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    alert: rule.id,
                    severity: rule.severity,
                    message,
                    stats,
                    timestamp: new Date().toISOString()
                })
            })
        } catch (error) {
            logger.error('Webhook send failed', { error: error.message })
        }
    }

    /**
     * Send Slack notification
     */
    async sendSlack(message, rule, stats) {
        try {
            const color = this.getColorForSeverity(rule.severity)
            await fetch(this.slackWebhook, {
                method: 'POST',
                body: JSON.stringify({
                    attachments: [{
                        color,
                        title: rule.description,
                        text: message,
                        fields: [
                            { title: 'Severity', value: rule.severity, short: true },
                            { title: 'Errors', value: stats.errorCount, short: true },
                            { title: 'Critical', value: stats.criticalCount, short: true },
                            { title: 'Timestamp', value: new Date().toISOString(), short: false }
                        ]
                    }]
                })
            })
        } catch (error) {
            logger.error('Slack notification failed', { error: error.message })
        }
    }

    /**
     * Get icon for severity level
     */
    getIconForSeverity(severity) {
        const icons = {
            info: 'ℹ️',
            warning: '⚠️',
            error: '❌',
            critical: '🔴'
        }
        return icons[severity] || '❓'
    }

    /**
     * Get color for severity level (for Slack)
     */
    getColorForSeverity(severity) {
        const colors = {
            info: '#2196F3',
            warning: '#FF9800',
            error: '#f44336',
            critical: '#9C27B0'
        }
        return colors[severity] || '#808080'
    }

    /**
     * Register callback for alert events
     */
    on(event, callback) {
        this.callbacks.set(event, callback)
    }

    /**
     * Get current metrics
     */
    getMetrics() {
        return { ...this.metrics }
    }

    /**
     * Get all active alerts
     */
    getActiveAlerts() {
        const active = []
        for (const [key, value] of alertHistory.entries()) {
            if (key.startsWith('alert_') && value.firedAt) {
                active.push({
                    id: key.replace('alert_', ''),
                    rule: value.rule,
                    firedAt: value.firedAt,
                    duration: Date.now() - value.firedAt
                })
            }
        }
        return active
    }

    /**
     * Request notification permission
     */
    async requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            const permission = await Notification.requestPermission()
            return permission === 'granted'
        }
        return Notification.permission === 'granted'
    }
}

// Global singleton instance
let alertServiceInstance = null

/**
 * Get or create global alert service
 */
export function getAlertService(options = {}) {
    if (!alertServiceInstance) {
        alertServiceInstance = new AlertService(options)
    }
    return alertServiceInstance
}

/**
 * Create composable for alerts
 */
export function useAlerts(options = {}) {
    const alertService = getAlertService(options)

    return {
        service: alertService,
        checkAlerts: (stats) => alertService.checkAlerts(stats),
        recordMetric: (type, data) => alertService.recordMetric(type, data),
        requestPermission: () => alertService.requestNotificationPermission(),
        getActiveAlerts: () => alertService.getActiveAlerts(),
        getMetrics: () => alertService.getMetrics(),
        on: (event, callback) => alertService.on(event, callback)
    }
}
