/**
 * Wrapper de compatibilidad para imports TypeScript.
 * Fuente canónica: `useApi.js`, que conserva la semántica legacy
 * (retornar payload desempaquetado y error normalizado).
 */

import { useApi as useApiLegacy } from './useApi.js'

export type UseApiComposable = ReturnType<typeof useApiLegacy>

export function useApi(): UseApiComposable {
  return useApiLegacy()
}
