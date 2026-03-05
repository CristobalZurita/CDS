import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  BUSINESS_TIMEZONE,
  formatDate,
  formatLocal,
  formatLocalES,
  formatTime,
  isToday,
  timeAgo,
  toLocal,
  toUTC,
} from '@/utils/timezone'

describe('timezone utils', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('handles null and invalid inputs', () => {
    expect(BUSINESS_TIMEZONE).toBe('America/Santiago')
    expect(toLocal(null)).toBeNull()
    expect(toLocal('invalid-date')).toBeNull()
    expect(toUTC(undefined)).toBeNull()
    expect(toUTC('invalid-date')).toBeNull()
    expect(formatLocal(null)).toBe('')
    expect(formatLocalES(undefined)).toBe('')
    expect(formatDate('invalid-date')).toBe('')
    expect(formatTime('invalid-date')).toBe('')
    expect(timeAgo(undefined)).toBe('')
    expect(isToday(null)).toBe(false)
  })

  it('formats dates for display and converts back to UTC', () => {
    const iso = '2026-03-05T15:30:00.000Z'
    const local = toLocal(iso)

    expect(local).toBeInstanceOf(Date)
    expect(toUTC(local)).toBe(iso)
    expect(formatLocal(iso)).toContain('2026')
    expect(formatLocalES(iso)).toContain('hrs')
    expect(formatDate(iso)).toContain('2026')
    expect(formatTime(iso)).toMatch(/^\d{2}:\d{2}$/)
  })

  it('computes relative time labels and today checks', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-03-05T12:00:00.000Z'))

    expect(timeAgo('2026-03-05T11:59:30.000Z')).toBe('hace un momento')
    expect(timeAgo('2026-03-05T11:30:00.000Z')).toBe('hace 30 min')
    expect(timeAgo('2026-03-05T10:00:00.000Z')).toBe('hace 2h')
    expect(timeAgo('2026-03-03T12:00:00.000Z')).toBe('hace 2d')

    const oldIso = '2025-12-01T12:00:00.000Z'
    expect(timeAgo(oldIso)).toBe(formatDate(oldIso))

    expect(isToday('2026-03-05T08:00:00.000Z')).toBe(true)
    expect(isToday('2026-03-04T23:00:00.000Z')).toBe(false)
  })
})
