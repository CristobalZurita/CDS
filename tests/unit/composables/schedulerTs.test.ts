import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useScheduler } from '@/composables/scheduler.ts'

describe('scheduler.ts', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    useScheduler().clearAll()
  })

  afterEach(() => {
    useScheduler().clearAll()
    vi.useRealTimers()
  })

  it('schedules timeout callbacks', () => {
    const scheduler = useScheduler()
    const callback = vi.fn()

    scheduler.schedule(callback, 100, 'quote')
    vi.advanceTimersByTime(99)
    expect(callback).not.toHaveBeenCalled()

    vi.advanceTimersByTime(1)
    expect(callback).toHaveBeenCalledTimes(1)
  })

  it('clears timeout and interval callbacks by tag', () => {
    const scheduler = useScheduler()
    const keepTimeout = vi.fn()
    const dropTimeout = vi.fn()
    const keepInterval = vi.fn()
    const dropInterval = vi.fn()

    scheduler.schedule(keepTimeout, 100, 'keep')
    scheduler.schedule(dropTimeout, 100, 'drop')
    scheduler.interval(keepInterval, 50, 'keep')
    scheduler.interval(dropInterval, 50, 'drop')

    scheduler.clearAllWithTag('drop')
    vi.advanceTimersByTime(120)

    expect(dropTimeout).not.toHaveBeenCalled()
    expect(dropInterval).not.toHaveBeenCalled()
    expect(keepTimeout).toHaveBeenCalledTimes(1)
    expect(keepInterval).toHaveBeenCalledTimes(2)
  })

  it('clears all pending callbacks', () => {
    const scheduler = useScheduler()
    const timeout = vi.fn()
    const interval = vi.fn()

    scheduler.schedule(timeout, 20, 'a')
    scheduler.interval(interval, 20, 'b')
    scheduler.clearAll()
    vi.advanceTimersByTime(100)

    expect(timeout).not.toHaveBeenCalled()
    expect(interval).not.toHaveBeenCalled()
  })
})
