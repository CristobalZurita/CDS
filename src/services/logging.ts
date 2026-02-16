/**
 * PHASE 8: Observability - Frontend Logging Service
 * Centralized logging, error tracking, performance monitoring
 */

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
}

export interface LogEntry {
  timestamp: string
  level: LogLevel
  message: string
  context?: Record<string, any>
  stackTrace?: string
  url?: string
  userAgent?: string
  userId?: number
}

export interface PerformanceMetric {
  name: string
  duration: number
  timestamp: string
  metadata?: Record<string, any>
}

class LoggingService {
  private logs: LogEntry[] = []
  private metrics: PerformanceMetric[] = []
  private maxLogs = 1000
  private maxMetrics = 500
  private remoteEndpoint = '/api/logs'

  /**
   * Log message at specified level
   */
  log(level: LogLevel, message: string, context?: Record<string, any>): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      url: window.location.href,
      userAgent: navigator.userAgent
    }

    this.logs.push(entry)
    if (this.logs.length > this.maxLogs) {
      this.logs.shift()
    }

    // Console output in development
    if (import.meta.env.DEV) {
      const color = this.getLevelColor(level)
      console.log(`%c[${level}]`, `color: ${color}; font-weight: bold;`, message, context)
    }

    // Send critical errors to backend
    if (level === LogLevel.ERROR || level === LogLevel.CRITICAL) {
      this.sendToBackend(entry)
    }
  }

  debug(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.DEBUG, message, context)
  }

  info(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, context)
  }

  warn(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.WARN, message, context)
  }

  error(message: string, context?: Record<string, any>, stackTrace?: string): void {
    const entry = { timestamp: new Date().toISOString(), level: LogLevel.ERROR, message, context, stackTrace, url: window.location.href, userAgent: navigator.userAgent }
    this.logs.push(entry)
    this.sendToBackend(entry)
  }

  critical(message: string, context?: Record<string, any>): void {
    const entry = { timestamp: new Date().toISOString(), level: LogLevel.CRITICAL, message, context, url: window.location.href, userAgent: navigator.userAgent }
    this.logs.push(entry)
    this.sendToBackend(entry)
  }

  /**
   * Track performance metric
   */
  trackMetric(name: string, duration: number, metadata?: Record<string, any>): void {
    const metric: PerformanceMetric = {
      name,
      duration,
      timestamp: new Date().toISOString(),
      metadata
    }

    this.metrics.push(metric)
    if (this.metrics.length > this.maxMetrics) {
      this.metrics.shift()
    }

    // Log slow operations (>1s)
    if (duration > 1000) {
      this.warn(`Slow operation: ${name} took ${duration}ms`, { duration, name })
    }
  }

  /**
   * Measure async operation
   */
  async measure<T>(name: string, fn: () => Promise<T>, metadata?: Record<string, any>): Promise<T> {
    const start = performance.now()
    try {
      const result = await fn()
      const duration = performance.now() - start
      this.trackMetric(name, duration, metadata)
      return result
    } catch (error) {
      const duration = performance.now() - start
      this.trackMetric(name, duration, { ...metadata, error: String(error) })
      throw error
    }
  }

  /**
   * Track API call
   */
  trackApiCall(method: string, url: string, duration: number, status: number): void {
    this.trackMetric(`API ${method} ${url}`, duration, { method, url, status })
  }

  /**
   * Track page navigation
   */
  trackPageNavigation(from: string, to: string): void {
    this.info(`Navigation: ${from} → ${to}`, { from, to })
  }

  /**
   * Track user action
   */
  trackUserAction(action: string, target: string, metadata?: Record<string, any>): void {
    this.info(`User action: ${action}`, { action, target, ...metadata })
  }

  /**
   * Track error
   */
  trackError(error: Error, context?: Record<string, any>): void {
    this.error(error.message, { ...context, name: error.name }, error.stack)
  }

  /**
   * Get all logs
   */
  getLogs(level?: LogLevel, limit?: number): LogEntry[] {
    let filtered = this.logs
    if (level) {
      filtered = filtered.filter(l => l.level === level)
    }
    if (limit) {
      filtered = filtered.slice(-limit)
    }
    return filtered
  }

  /**
   * Get performance metrics
   */
  getMetrics(name?: string, limit?: number): PerformanceMetric[] {
    let filtered = this.metrics
    if (name) {
      filtered = filtered.filter(m => m.name.includes(name))
    }
    if (limit) {
      filtered = filtered.slice(-limit)
    }
    return filtered
  }

  /**
   * Export logs for analysis
   */
  exportLogs(format: 'json' | 'csv' = 'json'): string {
    if (format === 'json') {
      return JSON.stringify(this.logs, null, 2)
    } else {
      const headers = ['timestamp', 'level', 'message', 'context']
      const rows = this.logs.map(l => [
        l.timestamp,
        l.level,
        l.message,
        JSON.stringify(l.context || {})
      ])
      return [headers, ...rows].map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n')
    }
  }

  /**
   * Clear logs
   */
  clearLogs(): void {
    this.logs = []
  }

  /**
   * Clear metrics
   */
  clearMetrics(): void {
    this.metrics = []
  }

  /**
   * Send logs to backend
   */
  private async sendToBackend(entry: LogEntry): Promise<void> {
    try {
      const response = await fetch(this.remoteEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry)
      })
      if (!response.ok) {
        console.error(`Failed to send log to backend: ${response.status}`)
      }
    } catch (error) {
      console.error('Error sending log to backend:', error)
    }
  }

  /**
   * Get color for log level
   */
  private getLevelColor(level: LogLevel): string {
    const colors: Record<LogLevel, string> = {
      [LogLevel.DEBUG]: '#7F8C8D',
      [LogLevel.INFO]: '#3498DB',
      [LogLevel.WARN]: '#F39C12',
      [LogLevel.ERROR]: '#E74C3C',
      [LogLevel.CRITICAL]: '#C0392B'
    }
    return colors[level] || '#000'
  }
}

export const logger = new LoggingService()

/**
 * Vue plugin for logging
 */
export function useLogging() {
  return {
    logger,
    log: logger.log.bind(logger),
    debug: logger.debug.bind(logger),
    info: logger.info.bind(logger),
    warn: logger.warn.bind(logger),
    error: logger.error.bind(logger),
    critical: logger.critical.bind(logger),
    trackMetric: logger.trackMetric.bind(logger),
    measure: logger.measure.bind(logger),
    trackApiCall: logger.trackApiCall.bind(logger),
    trackUserAction: logger.trackUserAction.bind(logger),
    trackError: logger.trackError.bind(logger)
  }
}
