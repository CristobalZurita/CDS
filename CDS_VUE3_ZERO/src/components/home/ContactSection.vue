<template>
  <section id="contact" class="home-section home-contact">
    <div class="section-inner container">
      <h2 class="section-title">Contacto</h2>

      <div class="contact-layout">

        <!-- Formulario -->
        <div class="contact-form-wrap">
          <h3>Envíanos un mensaje</h3>
          <form class="contact-form" @submit.prevent="submitContact" novalidate>
            <div class="form-field">
              <label for="cf-name"><i class="fas fa-signature"></i> Nombre</label>
              <input id="cf-name" v-model="form.name" type="text" placeholder="Tu nombre" required autocomplete="name" />
            </div>
            <div class="form-field">
              <label for="cf-email"><i class="fas fa-envelope"></i> Email</label>
              <input id="cf-email" v-model="form.email" type="email" placeholder="tu@email.com" required autocomplete="email" />
            </div>
            <div class="form-field">
              <label for="cf-subject"><i class="fas fa-pen-to-square"></i> Asunto</label>
              <input id="cf-subject" v-model="form.subject" type="text" placeholder="Asunto del mensaje" required />
            </div>
            <div class="form-field">
              <label for="cf-message"><i class="fas fa-comment"></i> Mensaje</label>
              <textarea id="cf-message" v-model="form.message" rows="5" placeholder="Describe tu consulta..." required></textarea>
            </div>

            <TurnstileWidget @verify="t => form.turnstile_token = t" />

            <p v-if="formError" class="form-msg form-msg-error">
              <i class="fas fa-triangle-exclamation"></i> {{ formError }}
            </p>
            <p v-if="formSuccess" class="form-msg form-msg-success">
              <i class="fas fa-circle-check"></i> Mensaje enviado. Te contactaremos pronto.
            </p>

            <button type="submit" class="btn-submit" :disabled="formSending">
              <i class="fas fa-envelope"></i>
              {{ formSending ? 'Enviando…' : 'Enviar mensaje' }}
            </button>
          </form>
        </div>

        <!-- Info + mapa -->
        <div class="contact-info-wrap">
          <div class="contact-card">
            <p><i class="fas fa-location-dot"></i> <strong>Eusebio Lillo 362, Valparaíso</strong></p>
            <p><i class="fas fa-phone"></i> <a href="tel:+56982957538">+56 9 8295 7538</a></p>
            <p><i class="fas fa-envelope"></i> <a href="mailto:contacto@cirujanodesintetizadores.com">contacto@cirujanodesintetizadores.com</a></p>
            <div class="contact-channels">
              <a href="https://wa.me/56982957538" target="_blank" rel="noopener noreferrer">
                <i class="fa-brands fa-whatsapp"></i> WhatsApp
              </a>
              <a href="https://www.instagram.com/cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer">
                <i class="fa-brands fa-instagram"></i> Instagram
              </a>
              <a href="https://www.facebook.com/Cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer">
                <i class="fa-brands fa-facebook"></i> Facebook
              </a>
            </div>
          </div>

          <div class="contact-map">
            <iframe
              src="https://www.google.com/maps?q=Eusebio+Lillo+362,+Valpara%C3%ADso,+Chile&output=embed"
              title="Ubicación del taller"
              loading="lazy"
              referrerpolicy="no-referrer-when-downgrade"
            ></iframe>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'
import TurnstileWidget from '@/components/widgets/TurnstileWidget.vue'

const form = ref({ name: '', email: '', subject: '', message: '', turnstile_token: '' })
const formSending = ref(false)
const formSuccess = ref(false)
const formError = ref('')

async function submitContact() {
  formError.value = ''
  formSuccess.value = false

  if (!form.value.name || !form.value.email || !form.value.subject || !form.value.message) {
    formError.value = 'Por favor completa todos los campos.'
    return
  }

  formSending.value = true
  try {
    await api.post('/contact/', {
      name: form.value.name,
      email: form.value.email,
      subject: form.value.subject,
      message: form.value.message,
      turnstile_token: form.value.turnstile_token,
    })
    formSuccess.value = true
    form.value = { name: '', email: '', subject: '', message: '', turnstile_token: '' }
  } catch {
    formError.value = 'Error al enviar el mensaje. Intenta de nuevo o contáctanos por WhatsApp.'
  } finally {
    formSending.value = false
  }
}
</script>

<style scoped src="./homeShared.css"></style>
<style scoped>
.home-contact { background: var(--cds-background-color); }

.contact-layout {
  display: grid;
  gap: clamp(1.4rem, 2.8vw, 2.4rem);
  align-items: start;
}

.contact-form-wrap,
.contact-info-wrap {
  padding: clamp(1.3rem, 2vw, 2rem);
  border-radius: clamp(1.15rem, 2vw, 1.7rem);
  background: var(--cds-white);
  border: 1px solid var(--cds-border-card);
  box-shadow: var(--cds-shadow-sm);
}

.contact-form-wrap h3 {
  margin: 0 0 1.25rem;
  font-size: var(--cds-text-xl);
  color: var(--cds-dark);
}

.contact-form { display: grid; gap: 1rem; }

.form-field { display: grid; gap: 0.4rem; }

.form-field label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-text-normal);
}

.form-field label i {
  color: var(--cds-primary);
  font-size: var(--cds-text-sm);
}

.form-field input,
.form-field textarea {
  width: 100%;
  min-height: 52px;
  padding: 0.85rem 1rem;
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-md);
  font-size: clamp(1rem, 0.92rem + 0.34vw, 1.18rem);
  font-family: inherit;
  color: var(--cds-text-normal);
  background: var(--cds-white);
  line-height: var(--cds-leading-normal);
  transition: border-color 0.15s;
}

.form-field input:focus,
.form-field textarea:focus {
  outline: none;
  border-color: var(--cds-primary);
}

.form-field textarea {
  resize: vertical;
  min-height: 140px;
}

.form-msg {
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: var(--cds-radius-sm);
  font-size: var(--cds-text-sm);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-msg-error {
  background: var(--cds-invalid-bg);
  color: var(--cds-invalid-text);
  border: 1px solid var(--cds-invalid-border);
}

.form-msg-success {
  background: var(--cds-valid-bg);
  color: var(--cds-valid-text);
  border: 1px solid var(--cds-valid-border);
}

.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 48px;
  padding: 0.85rem 1.5rem;
  border: none;
  border-radius: var(--cds-radius-pill);
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: clamp(1rem, 0.92rem + 0.34vw, 1.16rem);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
  transition: opacity 0.15s, transform 0.15s;
}

.btn-submit:not(:disabled):hover {
  transform: translateY(-1px);
}

.btn-submit:disabled { opacity: 0.65; cursor: not-allowed; }

.contact-info-wrap {
  display: grid;
  gap: 1rem;
}

.contact-card {
  background: var(--cds-light);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-lg);
  padding: 1.25rem;
  display: grid;
  gap: 0.75rem;
  margin: 0;
  width: 100%;
}

.contact-card p {
  margin: 0;
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: var(--cds-text-base);
  color: var(--cds-text-normal);
}

.contact-card p i { color: var(--cds-primary); flex-shrink: 0; margin-top: 0.1rem; }
.contact-card a { color: var(--cds-primary); text-decoration: none; }

.contact-channels {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--cds-border-soft);
}

.contact-channels a {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-text-normal);
  text-decoration: none;
}

.contact-channels a:hover { color: var(--cds-primary); }

.contact-map {
  border-radius: var(--cds-radius-lg);
  overflow: hidden;
  height: 320px;
  border: 1px solid var(--cds-border-card);
  box-shadow: var(--cds-shadow-sm);
}

.contact-map iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

@media (min-width: 900px) {
  .contact-layout { grid-template-columns: 1fr 1fr; }
}
</style>
