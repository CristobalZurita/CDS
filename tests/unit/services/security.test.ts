import { afterEach, describe, expect, it, vi } from 'vitest'

async function loadSecurity() {
  const sanitize = vi.fn((dirty: string) => `clean:${dirty}`)
  vi.resetModules()
  vi.doMock('dompurify', () => ({
    default: {
      sanitize,
    },
  }))
  const module = await import('@/services/security')
  return { ...module, sanitize }
}

describe('security service helpers', () => {
  afterEach(() => {
    document.head.innerHTML = ''
    vi.resetModules()
    vi.restoreAllMocks()
  })

  it('sanitizes HTML with the configured DOMPurify allowlist', async () => {
    const { sanitizeHtml, sanitize } = await loadSecurity()

    expect(sanitizeHtml('<p>safe</p>')).toBe('clean:<p>safe</p>')
    expect(sanitize).toHaveBeenCalledWith('<p>safe</p>', {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'],
      ALLOWED_ATTR: [],
    })
  })

  it('sanitizes URLs and reads the CSRF token from the document', async () => {
    const { sanitizeUrl, getCSRFToken } = await loadSecurity()
    document.head.innerHTML = '<meta name="csrf-token" content="csrf-123">'

    expect(sanitizeUrl('/dashboard')).toBe(`${window.location.origin}/dashboard`)
    expect(sanitizeUrl('https://example.com/ok')).toBe('https://example.com/ok')
    expect(sanitizeUrl('javascript:alert(1)')).toBe('')
    expect(sanitizeUrl('notaurl')).toBe(`${window.location.origin}/notaurl`)
    expect(getCSRFToken()).toBe('csrf-123')
  })

  it('validates user input with the declared frontend patterns', async () => {
    const { validateInput } = await loadSecurity()

    expect(validateInput('user@example.com', 'email')).toBe(true)
    expect(validateInput('https://example.com', 'url')).toBe(true)
    expect(validateInput('+56 9 8295 7538', 'phone')).toBe(true)
    expect(validateInput('ABC123', 'alphanumeric')).toBe(true)

    expect(validateInput('bad-email', 'email')).toBe(false)
    expect(validateInput('ftp://example.com', 'url')).toBe(false)
    expect(validateInput('abc-123', 'alphanumeric')).toBe(false)
  })

  it('returns the current security header contract and generates CSP nonces', async () => {
    const { checkSecurityHeaders, generateNonce, CSP_CONFIG, enforceHttps } = await loadSecurity()

    expect(checkSecurityHeaders()).toEqual({
      'content-security-policy': null,
      'x-content-type-options': null,
      'x-frame-options': null,
      'x-xss-protection': null,
      'strict-transport-security': null,
    })

    const nonce = generateNonce()
    expect(nonce).toMatch(/^[0-9a-f]{32}$/)
    expect(CSP_CONFIG['default-src']).toEqual(["'self'"])
    expect(CSP_CONFIG['connect-src']).toContain('https://api.example.com')

    const protocolBefore = window.location.protocol
    enforceHttps()
    expect(window.location.protocol).toBe(protocolBefore)
  })
})
