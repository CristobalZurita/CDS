import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import {
  resolveApiHost,
  toAbsoluteMediaUrl,
  resolveRepairPhotoUrl,
  hydrateRepairPhotos,
  revokeHydratedRepairPhotos,
} from '@/services/secureMedia'

describe('secureMedia service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.defineProperty(URL, 'createObjectURL', {
      configurable: true,
      writable: true,
      value: vi.fn(() => 'blob:photo-1'),
    })
    Object.defineProperty(URL, 'revokeObjectURL', {
      configurable: true,
      writable: true,
      value: vi.fn(),
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('resolves API host and absolute media URLs preserving absolute/data/blob paths', () => {
    const host = resolveApiHost()

    expect(host).toContain('http')
    expect(toAbsoluteMediaUrl('/uploads/signatures/a.png')).toContain('/uploads/signatures/a.png')
    expect(toAbsoluteMediaUrl('uploads/images/b.png')).toContain('/uploads/images/b.png')
    expect(toAbsoluteMediaUrl('https://cdn.example.com/c.png')).toBe('https://cdn.example.com/c.png')
    expect(toAbsoluteMediaUrl('blob:abc123')).toBe('blob:abc123')
    expect(toAbsoluteMediaUrl('data:image/png;base64,abc')).toBe('data:image/png;base64,abc')
    expect(toAbsoluteMediaUrl('')).toBe('')
  })

  it('resolves download URLs through API blob fetch and direct URLs without fetch', async () => {
    apiMock.get.mockResolvedValueOnce({
      data: new Blob(['binary'], { type: 'image/png' }),
    })

    const blobUrl = await resolveRepairPhotoUrl({
      photo_download_url: '/files/repairs/77',
    })
    const directUrl = await resolveRepairPhotoUrl({
      photo_url: '/uploads/repairs/repair-77/photo-1.png',
    })

    expect(apiMock.get).toHaveBeenCalledWith(
      expect.stringContaining('/files/repairs/77'),
      { responseType: 'blob' }
    )
    expect(URL.createObjectURL).toHaveBeenCalledTimes(1)
    expect(blobUrl).toBe('blob:photo-1')
    expect(directUrl).toContain('/uploads/repairs/repair-77/photo-1.png')
  })

  it('hydrates and revokes resolved repair photos correctly', async () => {
    apiMock.get.mockResolvedValueOnce({
      data: new Blob(['binary'], { type: 'image/png' }),
    })

    const hydrated = await hydrateRepairPhotos([
      { id: 1, photo_url: '/uploads/images/local.png' },
      { id: 2, photo_download_url: '/files/private/2' },
    ])

    expect(hydrated).toHaveLength(2)
    expect(hydrated[0].resolved_photo_url).toContain('/uploads/images/local.png')
    expect(hydrated[1].resolved_photo_url).toBe('blob:photo-1')

    revokeHydratedRepairPhotos(hydrated)

    expect(URL.revokeObjectURL).toHaveBeenCalledTimes(1)
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:photo-1')
  })
})
