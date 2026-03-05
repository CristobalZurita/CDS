/**
 * Compatibility wrapper for useApi composable
 * 
 * This file provides backward compatibility for code that imports `useApi()`.
 * The actual implementation has been migrated to `/src/services/api.ts`.
 * 
 * This composable re-exports the api service functions to maintain
 * compatibility with existing code while allowing gradual migration.
 */

import { 
  get, 
  post, 
  put, 
  patch, 
  deleteRequest, 
  handleApiError 
} from '@/services/api'
import type { ApiRequestConfig } from '@/services/api'
import type { AxiosResponse } from 'axios'
import type { ApiResponse } from '@/types/common'

export interface UseApiComposable {
  get: <T = any>(url: string, config?: ApiRequestConfig) => Promise<AxiosResponse<ApiResponse<T>>>
  post: <T = any>(url: string, data?: any, config?: ApiRequestConfig) => Promise<AxiosResponse<ApiResponse<T>>>
  put: <T = any>(url: string, data?: any, config?: ApiRequestConfig) => Promise<AxiosResponse<ApiResponse<T>>>
  patch: <T = any>(url: string, data?: any, config?: ApiRequestConfig) => Promise<AxiosResponse<ApiResponse<T>>>
  delete: <T = any>(url: string, config?: ApiRequestConfig) => Promise<AxiosResponse<ApiResponse<T>>>
  handleApiError: (error: unknown) => any
}

/**
 * useApi - Compatibility wrapper composable
 * 
 * @returns {UseApiComposable} API functions
 * 
 * @example
 * // Old code still works
 * const { get, post } = useApi()
 * const data = await get('/endpoint')
 * 
 * @example
 * // Or use the service directly (preferred)
 * import { get, post } from '@/services/api'
 * const data = await get('/endpoint')
 */
export function useApi(): UseApiComposable {
  return {
    get,
    post,
    put,
    patch,
    delete: deleteRequest,
    handleApiError
  }
}
