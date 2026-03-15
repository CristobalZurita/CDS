import { computed, reactive } from 'vue'
import { validators } from './useFormValidation'

export function useLoginValidation({ email, password, requires2fa, twoFactorCode }) {
  const errors = reactive({
    email: '',
    password: '',
    twoFactorCode: ''
  })

  const canSubmit = computed(() => {
    const hasEmail = validators.required(email.value) && validators.email(email.value)
    const hasPassword = String(password.value || '').length >= 1
    const hasTwoFactor = !requires2fa.value || String(twoFactorCode.value || '').trim().length >= 6
    return hasEmail && hasPassword && hasTwoFactor
  })

  function validate() {
    errors.email = ''
    errors.password = ''
    errors.twoFactorCode = ''

    if (!String(email.value || '').trim()) {
      errors.email = 'El email es requerido'
    } else if (!validators.email(email.value)) {
      errors.email = 'Email inválido'
    }

    if (!String(password.value || '')) {
      errors.password = 'La contraseña es requerida' // pragma: allowlist secret
    }

    if (requires2fa.value) {
      if (!String(twoFactorCode.value || '').trim()) {
        errors.twoFactorCode = 'El código 2FA es requerido'
      } else if (String(twoFactorCode.value).trim().length < 6) {
        errors.twoFactorCode = 'El código 2FA debe tener al menos 6 caracteres'
      }
    }

    return !errors.email && !errors.password && !errors.twoFactorCode
  }

  return {
    errors,
    canSubmit,
    validate
  }
}

export function useRegisterValidation(form) {
  const errors = reactive({
    email: '',
    username: '',
    full_name: '',
    password: ''
  })

  const canSubmit = computed(() => {
    const hasEmail = validators.required(form.email) && validators.email(form.email)
    const hasUser = String(form.username || '').trim().length >= 1
    const hasName = String(form.full_name || '').trim().length >= 1
    const hasPassword = String(form.password || '').length >= 8
    return hasEmail && hasUser && hasName && hasPassword
  })

  function validate() {
    errors.email = ''
    errors.username = ''
    errors.full_name = ''
    errors.password = ''

    if (!String(form.email || '').trim()) {
      errors.email = 'El email es requerido'
    } else if (!validators.email(form.email)) {
      errors.email = 'Email inválido'
    }

    if (!String(form.username || '').trim()) {
      errors.username = 'El usuario es requerido'
    }

    if (!String(form.full_name || '').trim()) {
      errors.full_name = 'El nombre completo es requerido'
    }

    if (!String(form.password || '')) {
      errors.password = 'La contraseña es requerida' // pragma: allowlist secret
    } else if (String(form.password).length < 8) {
      errors.password = 'La contraseña debe tener al menos 8 caracteres' // pragma: allowlist secret
    }

    return !errors.email && !errors.username && !errors.full_name && !errors.password
  }

  return {
    errors,
    canSubmit,
    validate
  }
}

export function usePasswordResetValidation({ mode, email, token, newPassword, confirmPassword }) {
  const errors = reactive({
    email: '',
    token: '',
    newPassword: '',
    confirmPassword: ''
  })

  const canSubmit = computed(() => {
    if (mode.value === 'request') {
      return validators.required(email.value) && validators.email(email.value)
    }

    const hasToken = String(token.value || '').trim().length >= 1
    const hasPassword = String(newPassword.value || '').length >= 8
    const passwordsMatch = String(newPassword.value || '') === String(confirmPassword.value || '')
    return hasToken && hasPassword && passwordsMatch
  })

  function validateRequest() {
    errors.email = ''
    if (!String(email.value || '').trim()) {
      errors.email = 'El email es requerido'
    } else if (!validators.email(email.value)) {
      errors.email = 'Email inválido'
    }
    return !errors.email
  }

  function validateReset() {
    errors.token = ''
    errors.newPassword = ''
    errors.confirmPassword = ''

    if (!String(token.value || '').trim()) {
      errors.token = 'El token es requerido'
    }

    if (!String(newPassword.value || '')) {
      errors.newPassword = 'La nueva contraseña es requerida' // pragma: allowlist secret
    } else if (String(newPassword.value).length < 8) {
      errors.newPassword = 'La nueva contraseña debe tener al menos 8 caracteres' // pragma: allowlist secret
    }

    if (!String(confirmPassword.value || '')) {
      errors.confirmPassword = 'Debes confirmar la contraseña' // pragma: allowlist secret
    } else if (String(newPassword.value || '') !== String(confirmPassword.value || '')) {
      errors.confirmPassword = 'Las contraseñas no coinciden' // pragma: allowlist secret
    }

    return !errors.token && !errors.newPassword && !errors.confirmPassword
  }

  return {
    errors,
    canSubmit,
    validateRequest,
    validateReset
  }
}
