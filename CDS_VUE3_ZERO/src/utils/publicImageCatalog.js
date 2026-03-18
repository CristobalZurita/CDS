/**
 * Compatibilidad explícita con el catálogo estático legacy.
 *
 * ZERO ya no usa listados hardcodeados ni image-mapping.json en runtime.
 * image-mapping.json puede seguir existiendo sólo como artefacto de auditoría,
 * pero no manda la resolución real de imágenes.
 * La fuente de verdad para URLs es cloudinary.js + cloudinaryContract.js.
 *
 * Este archivo se mantiene sólo como shim para imports legacy todavía posibles.
 * Código nuevo debe importar desde cloudinary.js o useCloudinary.ts.
 */

export const instrumentImagePaths = []
export const inventoryImagePaths = []
export const calculatorImagePaths = []
export const publicImagePaths = []

// Re-exportar desde cloudinary.js para mantener compatibilidad.
export {
  toCloudinaryUrl,
  toThumbnail,
  toOptimized,
  getCloudinaryUrlFromMapping,
} from './cloudinary.js'

export const instrumentCloudinaryUrls = []
export const inventoryCloudinaryUrls = []
export const calculatorCloudinaryUrls = []
