/**
 * Scheduler composable for task scheduling and appointment management
 */

import { ref } from 'vue'

export function useScheduler() {
  const appointments = ref([])
  const loading = ref(false)
  const error = ref(null)
  const tasks = ref(new Map())

  /**
   * Schedule a task
   * @param {function} callback - Function to execute
   * @param {number} delay - Delay in milliseconds
   * @param {string} tag - Tag to identify the task
   */
  const schedule = (callback, delay, tag = 'default') => {
    if (!tasks.value.has(tag)) {
      tasks.value.set(tag, [])
    }
    
    const timeoutId = setTimeout(() => {
      callback()
      removeTask(tag, timeoutId)
    }, delay)
    
    tasks.value.get(tag).push(timeoutId)
    return timeoutId
  }

  /**
   * Interval scheduler
   * @param {function} callback - Function to execute
   * @param {number} interval - Interval in milliseconds
   * @param {string} tag - Tag to identify the task
   */
  const interval = (callback, intervalMs, tag = 'default') => {
    if (!tasks.value.has(tag)) {
      tasks.value.set(tag, [])
    }
    
    const intervalId = setInterval(() => {
      callback()
    }, intervalMs)
    
    tasks.value.get(tag).push(intervalId)
    return intervalId
  }

  /**
   * Clear all tasks with a specific tag
   * @param {string} tag - Tag identifier
   */
  const clearAllWithTag = (tag) => {
    if (tasks.value.has(tag)) {
      const timeoutIds = tasks.value.get(tag)
      timeoutIds.forEach(id => {
        clearTimeout(id)
        clearInterval(id)
      })
      tasks.value.delete(tag)
    }
  }

  /**
   * Remove a specific task
   * @param {string} tag - Tag identifier
   * @param {number} timeoutId - Timeout ID to remove
   */
  const removeTask = (tag, timeoutId) => {
    if (tasks.value.has(tag)) {
      const timeoutIds = tasks.value.get(tag)
      const index = timeoutIds.indexOf(timeoutId)
      if (index > -1) {
        timeoutIds.splice(index, 1)
      }
      if (timeoutIds.length === 0) {
        tasks.value.delete(tag)
      }
    }
  }

  const fetchAppointments = async () => {
    loading.value = true
    try {
      appointments.value = []
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  const createAppointment = async (data) => {
    try {
      return { success: true }
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const updateAppointment = async (id, data) => {
    try {
      return { success: true }
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const deleteAppointment = async (id) => {
    try {
      return { success: true }
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  return {
    appointments,
    loading,
    error,
    schedule,
    interval,
    clearAllWithTag,
    removeTask,
    fetchAppointments,
    createAppointment,
    updateAppointment,
    deleteAppointment
  }
}
