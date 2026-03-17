<template>
  <section id="contacto" class="contact-section">
    <div class="contact-inner">

      <h2 class="contact-title">¿Tienes un sintetizador que necesita atención?</h2>
      <p class="contact-lead">
        Escríbenos y te respondemos a la brevedad.
        También puedes contactarnos directamente por WhatsApp o redes sociales.
      </p>

      <!-- Formulario -->
      <form class="contact-form" @submit.prevent="submitForm" novalidate>

        <div class="form-row">
          <div class="form-field">
            <label for="cf-name">Nombre</label>
            <input
              id="cf-name"
              v-model="form.name"
              type="text"
              placeholder="Tu nombre"
              autocomplete="name"
              :class="{ 'is-invalid': errors.name }"
            />
            <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
          </div>

          <div class="form-field">
            <label for="cf-email">Correo electrónico</label>
            <input
              id="cf-email"
              v-model="form.email"
              type="email"
              placeholder="tu@correo.cl"
              autocomplete="email"
              :class="{ 'is-invalid': errors.email }"
            />
            <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
          </div>
        </div>

        <div class="form-field">
          <label for="cf-instrument">Instrumento (opcional)</label>
          <input
            id="cf-instrument"
            v-model="form.instrument"
            type="text"
            placeholder="Ej: Juno-106, Korg MS-20, Prophet-5…"
          />
        </div>

        <div class="form-field">
          <label for="cf-message">Mensaje</label>
          <textarea
            id="cf-message"
            v-model="form.message"
            rows="5"
            placeholder="Cuéntanos qué le pasa a tu instrumento, qué servicio necesitas, o cualquier consulta…"
            :class="{ 'is-invalid': errors.message }"
          ></textarea>
          <span v-if="errors.message" class="field-error">{{ errors.message }}</span>
        </div>

        <!-- Feedback de envío -->
        <div v-if="status === 'success'" class="form-feedback form-feedback--ok">
          <i class="fas fa-circle-check"></i>
          Mensaje enviado. ¡Te respondemos pronto!
        </div>
        <div v-if="status === 'error'" class="form-feedback form-feedback--err">
          <i class="fas fa-circle-xmark"></i>
          Hubo un error al enviar. Intenta por WhatsApp o escríbenos directo al correo.
        </div>

        <button
          type="submit"
          class="btn-submit"
          :disabled="sending"
        >
          <i v-if="sending" class="fas fa-spinner fa-spin"></i>
          <i v-else class="fas fa-paper-plane"></i>
          {{ sending ? 'Enviando…' : 'Enviar mensaje' }}
        </button>

      </form>

      <!-- Contacto directo -->
      <div class="contact-direct">
        <a href="https://wa.me/56982957538" target="_blank" rel="noopener noreferrer" class="direct-link direct-link--wa">
          <i class="fa-brands fa-whatsapp"></i>
          +56 9 8295 7538
        </a>
        <a href="mailto:cirujanodesintetizadores@gmail.com" class="direct-link">
          <i class="fas fa-envelope"></i>
          cirujanodesintetizadores@gmail.com
        </a>
        <a href="https://www.instagram.com/cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer" class="direct-link">
          <i class="fa-brands fa-instagram"></i>
          @cirujanodesintetizadores
        </a>
      </div>

    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'

const form = reactive({ name: '', email: '', instrument: '', message: '' })
const errors = reactive({ name: '', email: '', message: '' })
const sending = ref(false)
const status = ref('') // '' | 'success' | 'error'

function validate() {
  errors.name    = form.name.trim()    ? '' : 'El nombre es obligatorio'
  errors.email   = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email) ? '' : 'Correo inválido'
  errors.message = form.message.trim() ? '' : 'Escribe tu mensaje'
  return !errors.name && !errors.email && !errors.message
}

async function submitForm() {
  if (!validate()) return

  sending.value = true
  status.value  = ''

  try {
    const body = new FormData()
    body.append('name',       form.name.trim())
    body.append('email',      form.email.trim())
    body.append('instrument', form.instrument.trim())
    body.append('message',    form.message.trim())

    const res = await fetch('/mail.php', { method: 'POST', body })
    const json = await res.json()

    if (res.ok && json.ok) {
      status.value = 'success'
      form.name = form.email = form.instrument = form.message = ''
    } else {
      status.value = 'error'
    }
  } catch {
    status.value = 'error'
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
.contact-section {
  background: var(--cds-dark);
  padding: clamp(3.5rem, 6vw, 5rem) clamp(1.25rem, 5vw, 3rem);
}

.contact-inner {
  max-width: min(1690px, 94vw);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-lg);
}

.contact-title {
  font-family: var(--cds-headings-font-family);
  font-size: var(--cds-text-xl);
  font-weight: var(--cds-font-bold);
  color: var(--cds-white);
  line-height: var(--cds-leading-tight);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.contact-lead {
  font-size: var(--cds-text-lg);
  color: var(--cds-light);
  opacity: 0.72;
  line-height: var(--cds-leading-normal);
  margin-top: calc(-1 * var(--cds-space-sm));
}

/* Form */
.contact-form {
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-md);
}

.form-row {
  display: grid;
  gap: var(--cds-space-md);
  grid-template-columns: 1fr;
}

@media (min-width: 560px) {
  .form-row { grid-template-columns: 1fr 1fr; }
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-xs);
}

.form-field label {
  font-size: var(--cds-text-md);
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--cds-light);
  opacity: 0.75;
}

.form-field input,
.form-field textarea {
  background: color-mix(in srgb, var(--cds-white) 6%, transparent);
  border: 1px solid color-mix(in srgb, var(--cds-light) 22%, transparent);
  border-radius: var(--cds-radius-sm);
  padding: var(--cds-space-sm) var(--cds-space-md);
  color: var(--cds-white);
  font-size: var(--cds-text-md);
  font-family: var(--cds-font-family-base);
  transition: border-color 0.15s, box-shadow 0.15s;
  resize: vertical;
}

.form-field input::placeholder,
.form-field textarea::placeholder {
  color: color-mix(in srgb, var(--cds-light) 35%, transparent);
}

.form-field input:focus,
.form-field textarea:focus {
  outline: none;
  border-color: var(--cds-primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--cds-primary) 20%, transparent);
}

.form-field input.is-invalid,
.form-field textarea.is-invalid {
  border-color: var(--cds-danger);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--cds-danger) 15%, transparent);
}

.field-error {
  font-size: var(--cds-text-sm);
  color: color-mix(in srgb, var(--cds-danger) 70%, var(--cds-white));
  font-weight: var(--cds-font-medium);
}

/* Feedback */
.form-feedback {
  display: flex;
  align-items: center;
  gap: var(--cds-space-sm);
  padding: var(--cds-space-sm) var(--cds-space-md);
  border-radius: var(--cds-radius-sm);
  font-weight: var(--cds-font-semibold);
  font-size: var(--cds-text-md);
}

.form-feedback--ok  {
  background: color-mix(in srgb, var(--cds-success) 15%, transparent);
  color:       color-mix(in srgb, var(--cds-success) 60%, var(--cds-white));
  border: 1px solid color-mix(in srgb, var(--cds-success) 30%, transparent);
}
.form-feedback--err {
  background: color-mix(in srgb, var(--cds-danger) 12%, transparent);
  color:       color-mix(in srgb, var(--cds-danger)  70%, var(--cds-white));
  border: 1px solid color-mix(in srgb, var(--cds-danger) 25%, transparent);
}

/* Submit */
.btn-submit {
  display: inline-flex;
  align-items: center;
  gap: var(--cds-space-xs);
  align-self: flex-start;
  min-height: 3.5rem;
  padding: var(--cds-space-sm) var(--cds-space-xl);
  border: none;
  border-radius: var(--cds-radius-pill);
  background: var(--cds-primary);
  color: var(--cds-white);
  font-family: var(--cds-font-family-base);
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: transform 0.15s, opacity 0.15s, box-shadow 0.15s;
  box-shadow: 0 4px 18px color-mix(in srgb, var(--cds-primary) 30%, transparent);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px color-mix(in srgb, var(--cds-primary) 40%, transparent);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Contacto directo */
.contact-direct {
  display: flex;
  flex-wrap: wrap;
  gap: var(--cds-space-sm) var(--cds-space-xl);
  padding-top: var(--cds-space-sm);
  border-top: 1px solid color-mix(in srgb, var(--cds-light) 12%, transparent);
}

.direct-link {
  display: inline-flex;
  align-items: center;
  gap: var(--cds-space-xs);
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  color: color-mix(in srgb, var(--cds-light) 72%, transparent);
  text-decoration: none;
  transition: color 0.15s;
}

.direct-link:hover { color: var(--cds-white); }

.direct-link--wa { color: var(--cds-whatsapp); }
.direct-link--wa:hover { color: color-mix(in srgb, var(--cds-whatsapp) 60%, var(--cds-white)); }

/* ── PC: 2 columnas — izquierda info, derecha formulario ── */
@media (min-width: 900px) {
  .contact-inner {
    display: grid;
    grid-template-columns: 1fr 1.4fr;
    grid-template-areas:
      "title  form"
      "lead   form"
      "direct form";
    column-gap: var(--cds-space-xl);
    row-gap: var(--cds-space-md);
    align-items: start;
  }
  .contact-title  { grid-area: title; }
  .contact-lead   { grid-area: lead; margin-top: 0; }
  .contact-form   { grid-area: form; grid-row: 1 / 4; }
  .contact-direct { grid-area: direct; }
}
</style>
