/**
 * TEMPO MAESTRO — Frontend timezone utility (ADITIVO)
 * ====================================================
 *
 * Contraparte frontend del módulo backend `app/core/timezone.py`.
 *
 * Regla:
 *   - La API siempre envía y espera timestamps en UTC (ISO 8601 con 'Z').
 *   - El frontend convierte UTC → America/Santiago SOLO para mostrar al usuario.
 *   - Al enviar datos a la API, se convierte a UTC.
 *
 * Uso:
 *   import { toLocal, toUTC, formatLocal, formatLocalES } from '@/utils/timezone'
 *
 *   // Mostrar fecha de la API al usuario:
 *   const display = formatLocal(repair.created_at)  // "22/02/2026 14:00"
 *
 *   // Enviar fecha del usuario a la API:
 *   const utcISO = toUTC(userPickedDate)  // "2026-02-22T17:00:00Z"
 */

/** Zona horaria del negocio (Chile continental) */
export const BUSINESS_TIMEZONE = 'America/Santiago'

/**
 * Convierte un timestamp (string ISO o Date) a Date en hora local de Chile.
 * Para display solamente.
 */
export function toLocal(input: string | Date | null | undefined): Date | null {
  if (!input) return null
  const d = typeof input === 'string' ? new Date(input) : input
  if (isNaN(d.getTime())) return null
  return d // JS Date ya contiene el instante UTC; al formatear con timezone se muestra local
}

/**
 * Convierte un Date local a string ISO UTC con 'Z' para enviar a la API.
 */
export function toUTC(input: Date | string | null | undefined): string | null {
  if (!input) return null
  const d = typeof input === 'string' ? new Date(input) : input
  if (isNaN(d.getTime())) return null
  return d.toISOString() // Siempre retorna UTC con 'Z'
}

/**
 * Formatea un timestamp para mostrar al usuario en formato chileno.
 *
 * @param input - ISO string o Date
 * @param options - Opciones de formato (default: fecha + hora)
 * @returns String formateado como "22/02/2026 14:00"
 */
export function formatLocal(
  input: string | Date | null | undefined,
  options?: Intl.DateTimeFormatOptions
): string {
  if (!input) return ''
  const d = typeof input === 'string' ? new Date(input) : input
  if (isNaN(d.getTime())) return ''

  const defaultOptions: Intl.DateTimeFormatOptions = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: BUSINESS_TIMEZONE,
  }

  return new Intl.DateTimeFormat('es-CL', options || defaultOptions).format(d)
}

/**
 * Formatea fecha en español chileno largo: "22 de febrero de 2026, 14:00 hrs"
 */
export function formatLocalES(input: string | Date | null | undefined): string {
  if (!input) return ''
  const d = typeof input === 'string' ? new Date(input) : input
  if (isNaN(d.getTime())) return ''

  const options: Intl.DateTimeFormatOptions = {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: BUSINESS_TIMEZONE,
  }

  return new Intl.DateTimeFormat('es-CL', options).format(d) + ' hrs'
}

/**
 * Formatea solo la fecha (sin hora): "22/02/2026"
 */
export function formatDate(input: string | Date | null | undefined): string {
  if (!input) return ''
  const d = typeof input === 'string' ? new Date(input) : input
  if (isNaN(d.getTime())) return ''

  return new Intl.DateTimeFormat('es-CL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    timeZone: BUSINESS_TIMEZONE,
  }).format(d)
}

/**
 * Formatea solo la hora: "14:00"
 */
export function formatTime(input: string | Date | null | undefined): string {
  if (!input) return ''
  const d = typeof input === 'string' ? new Date(input) : input
  if (isNaN(d.getTime())) return ''

  return new Intl.DateTimeFormat('es-CL', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: BUSINESS_TIMEZONE,
  }).format(d)
}

/**
 * Retorna "hace X minutos/horas/días" en español.
 * Útil para timestamps recientes (logs, actividad).
 */
export function timeAgo(input: string | Date | null | undefined): string {
  if (!input) return ''
  const d = typeof input === 'string' ? new Date(input) : input
  if (isNaN(d.getTime())) return ''

  const now = Date.now()
  const diffMs = now - d.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)

  if (diffSec < 60) return 'hace un momento'
  if (diffMin < 60) return `hace ${diffMin} min`
  if (diffHour < 24) return `hace ${diffHour}h`
  if (diffDay < 30) return `hace ${diffDay}d`
  return formatDate(d)
}

/**
 * Verifica si un timestamp es hoy (en zona horaria de Chile).
 */
export function isToday(input: string | Date | null | undefined): boolean {
  if (!input) return false
  const d = typeof input === 'string' ? new Date(input) : input
  if (isNaN(d.getTime())) return false

  const todayStr = new Intl.DateTimeFormat('en-CA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    timeZone: BUSINESS_TIMEZONE,
  }).format(new Date())

  const inputStr = new Intl.DateTimeFormat('en-CA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    timeZone: BUSINESS_TIMEZONE,
  }).format(d)

  return todayStr === inputStr
}
