/**
 * Wrapper de compatibilidad para imports legacy en JavaScript.
 * La implementacion autoritativa vive en `secureMedia.ts`.
 */

export {
  resolveApiHost,
  toAbsoluteMediaUrl,
  resolveRepairPhotoUrl,
  hydrateRepairPhotos,
  revokeHydratedRepairPhotos,
} from './secureMedia.ts'
