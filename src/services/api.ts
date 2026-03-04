/**
 * Composable useApi.ts - API client wrapper with TypeScript
 * MEJORADO: HttpOnly cookies (no localStorage), retry logic, timeout
 */

import type { AxiosInstance, AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import type { ApiResponse, ApiErrorResponse } from '@/types/common';
import axios from 'axios';

export const API_URL = import.meta.env.VITE_API_URL as string || 'http://localhost:8000/api/v1';
const API_TIMEOUT = 30000; // 30 segundos
const MAX_RETRIES = 3;

/**
 * Crear instancia de axios con configuración
 */
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT,
  withCredentials: true, // ✅ IMPORTANTE: Enviar cookies (HttpOnly)
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor - Agregar CSRF token
 */
api.interceptors.request.use((config) => {
  // Obtener CSRF token del meta tag
  const csrfMeta = document.querySelector('meta[name="csrf-token"]');
  if (csrfMeta) {
    config.headers['X-CSRF-Token'] = csrfMeta.getAttribute('content') || '';
  }

  // Compatibilidad aditiva: si existe token legacy en localStorage, adjuntarlo.
  const accessToken = localStorage.getItem('access_token');
  if (accessToken && !config.headers?.Authorization) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  // Los navegadores bloquean sobrescribir User-Agent; solo adjuntarlo fuera del runtime web.
  if (typeof window === 'undefined') {
    config.headers['User-Agent'] = `CirujanoFront/${import.meta.env.VITE_APP_VERSION as string || '1.0.0'}`;
  }

  return config;
});

/**
 * Response interceptor - Manejar errores globales y retries
 */
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as AxiosRequestConfig & { retryCount?: number };

    // Evitar retries en ciertos códigos de error
    if (!config || ![408, 429, 500, 502, 503, 504].includes(error.response?.status || 0)) {
      return Promise.reject(error);
    }

    // Contar reintentos
    config.retryCount = config.retryCount || 0;

    // Si ya intentamos MAX_RETRIES, fallar
    if (config.retryCount >= MAX_RETRIES) {
      return Promise.reject(error);
    }

    config.retryCount++;

    // Esperar con backoff exponencial
    const delay = Math.pow(2, config.retryCount) * 1000;
    await new Promise((resolve) => setTimeout(resolve, delay));

    // Reintentar
    return api(config);
  }
);

/**
 * Tipos genéricos para métodos HTTP
 */

export type ApiRequestConfig<T = any> = AxiosRequestConfig<T> & {
  retryCount?: number;
};

/**
 * GET request
 */
export async function get<T = any>(
  url: string,
  config?: ApiRequestConfig
): Promise<AxiosResponse<ApiResponse<T>>> {
  return api.get<ApiResponse<T>>(url, config);
}

/**
 * POST request
 */
export async function post<T = any>(
  url: string,
  data?: any,
  config?: ApiRequestConfig
): Promise<AxiosResponse<ApiResponse<T>>> {
  return api.post<ApiResponse<T>>(url, data, config);
}

/**
 * PUT request
 */
export async function put<T = any>(
  url: string,
  data?: any,
  config?: ApiRequestConfig
): Promise<AxiosResponse<ApiResponse<T>>> {
  return api.put<ApiResponse<T>>(url, data, config);
}

/**
 * PATCH request
 */
export async function patch<T = any>(
  url: string,
  data?: any,
  config?: ApiRequestConfig
): Promise<AxiosResponse<ApiResponse<T>>> {
  return api.patch<ApiResponse<T>>(url, data, config);
}

/**
 * DELETE request
 */
export async function deleteRequest<T = any>(
  url: string,
  config?: ApiRequestConfig
): Promise<AxiosResponse<ApiResponse<T>>> {
  return api.delete<ApiResponse<T>>(url, config);
}

/**
 * Error handler - Normalizar errores de API
 */
export function handleApiError(error: unknown): ApiErrorResponse {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiResponse | undefined;
    const errorInfo = data?.error;
    return {
      code: errorInfo?.code || 'UNKNOWN_ERROR',
      message: errorInfo?.message || error.message || 'Unknown error occurred',
      statusCode: error.response?.status || 500,
      details: errorInfo?.details,
    };
  }

  return {
    code: 'UNKNOWN_ERROR',
    message: error instanceof Error ? error.message : 'Unknown error',
    statusCode: 500,
  };
}

/**
 * Health check - Verificar conectividad con API
 */
export async function healthCheck(): Promise<boolean> {
  try {
    const response = await api.get('/health', { timeout: 5000 });
    return response.status === 200;
  } catch {
    return false;
  }
}

export { api };
export default api;
