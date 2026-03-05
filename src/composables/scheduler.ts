/**
 * Created by Ryan Balieiro on 03.05.2025
 * Bulk manager for timeouts and intervals.
 */

type TaggedTimeout = {
  id: ReturnType<typeof setTimeout>;
  tag: string | undefined;
};

type TaggedInterval = {
  id: ReturnType<typeof setInterval>;
  tag: string | undefined;
};

const timeouts: TaggedTimeout[] = [];
const intervals: TaggedInterval[] = [];

export const useScheduler = () => {
  /**
   * @param {function} callback
   * @param {Number} timeInMilliseconds
   * @param {string} tag
   */
  const schedule = (callback: () => void, timeInMilliseconds: number, tag?: string): void => {
    const timeoutId = setTimeout(callback, timeInMilliseconds);
    timeouts.push({ id: timeoutId, tag: tag });
  };

  /**
   * @param {function} callback
   * @param {Number} timeInMilliseconds
   * @param {string} tag
   */
  const interval = (callback: () => void, timeInMilliseconds: number, tag?: string): void => {
    const intervalId = setInterval(callback, timeInMilliseconds);
    intervals.push({ id: intervalId, tag: tag });
  };

  /**
   * @param {String} tag
   */
  const clearAllWithTag = (tag: string): void => {
    for (let i = timeouts.length - 1; i >= 0; i--) {
      if (timeouts[i].tag === tag) {
        clearTimeout(timeouts[i].id);
        timeouts.splice(i, 1);
      }
    }

    for (let i = intervals.length - 1; i >= 0; i--) {
      if (intervals[i].tag === tag) {
        clearInterval(intervals[i].id);
        intervals.splice(i, 1);
      }
    }
  };

  /**
   * @return {void}
   */
  const clearAll = (): void => {
    timeouts.forEach(timeout => {
      clearTimeout(timeout.id);
    });

    intervals.forEach(interval => {
      clearInterval(interval.id);
    });

    timeouts.length = 0;
    intervals.length = 0;
  };

  return {
    schedule,
    interval,
    clearAllWithTag,
    clearAll
  };
};
