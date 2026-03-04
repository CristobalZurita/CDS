/**
 * useMonitoring - Composable for application monitoring
 * Tracks performance, errors, user actions, and triggers alerts
 */

import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { buildLoggingRequestHeaders, logger } from '@/services/logging'
import { useAlerts } from '@/services/alerts'

interface MonitoringStats {
  pageLoadTime: number
  apiCallCount: number
  errorCount: number
  slowOperations: number
  lastUpdated: string
}

export function useMonitoring() {
  const router = useRouter()
  const stats = ref<MonitoringStats>({
    pageLoadTime: 0,
    apiCallCount: 0,
    errorCount: 0,
    slowOperations: 0,
    lastUpdated: new Date().toISOString()
  })

  let pageLoadStart = performance.now()

  /**
   * Track page load performance
   */
  const trackPageLoad = () => {
    const loadTime = performance.now() - pageLoadStart
    logger.trackMetric('page_load', loadTime)
    
    if (loadTime > 2000) {
      logger.warn(`Slow page load: ${loadTime.toFixed(0)}ms`, { loadTime })
    }

    stats.value.pageLoadTime = loadTime
  }

  /**
   * Setup error tracking
   */
  const setupErrorTracking = () => {
    window.addEventListener('error', (event) => {
      logger.trackError(event.error)
      stats.value.errorCount++
    })

    window.addEventListener('unhandledrejection', (event) => {
      logger.error('Unhandled promise rejection', {
        reason: event.reason
      })
      stats.value.errorCount++
    })
  }

  /**
   * Setup route tracking
   */
  const setupRouteTracking = () => {
    let previousRoute = router.currentRoute.value.path

    router.afterEach((to, from) => {
      logger.trackPageNavigation(from.path, to.path)
      pageLoadStart = performance.now()
    })
  }

  /**
   * Setup performance observer
   */
  const setupPerformanceObserver = () => {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.duration > 1000) {
              logger.warn(`Slow task: ${entry.name} (${entry.duration.toFixed(0)}ms)`)
              stats.value.slowOperations++
            }
          }
        })

        observer.observe({ entryTypes: ['longtask', 'measure'] })
      } catch (e) {
        logger.debug('PerformanceObserver not supported')
      }
    }
  }

  /**
   * Setup network monitoring (if available)
   */
  const setupNetworkMonitoring = () => {
    // Intercept fetch calls if possible
    const originalFetch = window.fetch
    let apiCallCount = 0

    window.fetch = function (...args) {
      const start = performance.now()
      apiCallCount++

      return originalFetch.apply(this, args).then((response) => {
        const duration = performance.now() - start
        const url = typeof args[0] === 'string' ? args[0] : args[0]?.url
        const method = (typeof args[1] === 'object' ? args[1]?.method : undefined) || 'GET'

        logger.trackApiCall(method, String(url), duration, response.status)
        stats.value.apiCallCount = apiCallCount

        return response
      })
    }
  }

  /**
   * Get current statistics
   */
  const getStats = (): MonitoringStats => {
    stats.value.lastUpdated = new Date().toISOString()
    return { ...stats.value }
  }

  /**
   * Send stats to backend
   */
  const sendStats = async () => {
    try {
      await fetch('/api/metrics', {
        method: 'POST',
        headers: buildLoggingRequestHeaders(true),
        body: JSON.stringify({
          name: 'app_stats',
          duration: stats.value.pageLoadTime,
          metadata: {
            apiCalls: stats.value.apiCallCount,
            errors: stats.value.errorCount,
            slowOps: stats.value.slowOperations
          }
        })
      })
    } catch (error) {
      logger.debug('Failed to send stats', { error: String(error) })
    }
  }

  /**
   * Setup monitoring on component mount
   */
  onMounted(() => {
    const { service: alertService, requestPermission } = useAlerts()
    
    setupErrorTracking()
    setupRouteTracking()
    setupPerformanceObserver()
    setupNetworkMonitoring()

    // Request notification permission for alerts
    requestPermission().catch(() => {
      logger.debug('Notifications not permitted')
    })

    // Track page load when mounted
    setTimeout(trackPageLoad, 0)

    // Periodically send stats and check alerts
    const interval = setInterval(async () => {
      await sendStats()
      
      // Fetch latest stats from backend and check alerts
      try {
        const response = await fetch('/api/logs/stats', {
          headers: buildLoggingRequestHeaders(false),
        })
        if (response.ok) {
          const backendStats = await response.json()
          await alertService.checkAlerts(backendStats)
        }
      } catch (error) {
        logger.debug('Failed to check alerts', { error: String(error) })
      }
    }, 60000) // Every minute

    onUnmounted(() => clearInterval(interval))
  })

  return {
    stats,
    trackPageLoad,
    getStats,
    sendStats
  }
}
