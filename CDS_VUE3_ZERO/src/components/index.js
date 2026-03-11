/**
 * ÍNDICE MAESTRO DE COMPONENTES
 * =============================
 * 
 * Importación centralizada de todos los componentes del sistema.
 * 
 * Uso:
 *   import { BaseButton, BaseCard, FormField, DataTable } from '@/components'
 *   import { BaseInput, BaseSelect } from '@/components/base'
 *   import { PhotoUpload } from '@/components/business'
 */

// Componentes Base (Atómicos)
export * from './base'

// Componentes Compuestos (Moléculas/Organismos)
export * from './composite'

// Componentes de Negocio (Dominio específico)
export * from './business'

// Componentes de Auth
export * from './auth'

// Componentes UI legacy (mantener compatibilidad)
export * from './ui'
