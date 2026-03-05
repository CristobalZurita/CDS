import { expect, type Page } from '@playwright/test'

const frontendOrigin = new URL(process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5174').origin
const apiOrigin = new URL(process.env.PLAYWRIGHT_API_URL || 'http://127.0.0.1:8001/api/v1').origin

function alternateLocalhostOrigin(origin: string) {
  if (origin.includes('127.0.0.1')) {
    return origin.replace('127.0.0.1', 'localhost')
  }
  if (origin.includes('localhost')) {
    return origin.replace('localhost', '127.0.0.1')
  }
  return origin
}

type BrowserErrorTracker = {
  consoleErrors: string[]
  pageErrors: string[]
  requestFailures: string[]
  responseFailures: string[]
}

const relevantOrigins = Array.from(
  new Set([
    frontendOrigin,
    alternateLocalhostOrigin(frontendOrigin),
    apiOrigin,
    alternateLocalhostOrigin(apiOrigin),
  ])
)

function isRelevantUrl(url: string) {
  return relevantOrigins.some((origin) => url.startsWith(origin))
}

function isIgnorableRequestFailure(errorText: string | undefined) {
  return (errorText || '').includes('net::ERR_ABORTED')
}

export function trackBrowserErrors(page: Page): BrowserErrorTracker {
  const consoleErrors: string[] = []
  const pageErrors: string[] = []
  const requestFailures: string[] = []
  const responseFailures: string[] = []

  page.on('console', (message) => {
    if (message.type() === 'error') {
      consoleErrors.push(message.text())
    }
  })

  page.on('pageerror', (error) => {
    pageErrors.push(error.message)
  })

  page.on('requestfailed', (request) => {
    if (!isRelevantUrl(request.url())) {
      return
    }
    const errorText = request.failure()?.errorText
    if (isIgnorableRequestFailure(errorText)) {
      return
    }
    requestFailures.push(`${request.method()} ${request.url()} :: ${errorText || 'request failed'}`)
  })

  page.on('response', (response) => {
    if (response.status() < 400 || !isRelevantUrl(response.url())) {
      return
    }
    responseFailures.push(`${response.status()} ${response.request().method()} ${response.url()}`)
  })

  return { consoleErrors, pageErrors, requestFailures, responseFailures }
}

export async function waitForAppToSettle(page: Page) {
  await page.waitForLoadState('domcontentloaded')
  await page.waitForTimeout(400)
}

export async function expectNoBrowserErrors(tracker: BrowserErrorTracker) {
  expect(tracker.pageErrors).toEqual([])
  expect(tracker.consoleErrors).toEqual([])
  expect(tracker.requestFailures).toEqual([])
  expect(tracker.responseFailures).toEqual([])
}
