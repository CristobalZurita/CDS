import { chromium } from '@playwright/test'

const browser = await chromium.launch()
const page = await browser.newPage()

const errors = []
const warnings = []
const logs = []

page.on('console', msg => {
  const text = msg.text()
  const type = msg.type()

  if (type === 'error') {
    errors.push(text)
    console.log(`❌ ERROR: ${text}`)
  } else if (type === 'warning') {
    warnings.push(text)
    console.log(`⚠️  WARNING: ${text}`)
  } else {
    logs.push(text)
    console.log(`ℹ️  LOG: ${text}`)
  }
})

page.on('pageerror', error => {
  console.log(`💥 PAGE ERROR: ${error.message}`)
  errors.push(error.message)
})

page.on('requestfailed', request => {
  console.log(`🚫 FAILED REQUEST: ${request.url()} - ${request.failure().errorText}`)
})

try {
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' })

  const html = await page.content()
  const appContent = await page.locator('#app').innerHTML()

  console.log('\n📊 SUMMARY:')
  console.log(`Errors: ${errors.length}`)
  console.log(`Warnings: ${warnings.length}`)
  console.log(`App innerHTML length: ${appContent.length}`)
  console.log(`App is empty: ${appContent.trim() === ''}`)

} catch (e) {
  console.log(`Failed to load page: ${e.message}`)
}

await browser.close()
