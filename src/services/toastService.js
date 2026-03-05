/**
 * Wrapper de compatibilidad para imports legacy en JavaScript.
 * La implementacion autoritativa vive en `toastService.ts`.
 */

export {
  setToastComponent,
  getToastComponent,
  showToast,
  showSuccess,
  showError,
  showWarning,
  showInfo,
} from './toastService.ts'
