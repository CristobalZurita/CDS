<template>
  <section id="contact" class="home-section home-contact">
    <div class="section-inner">
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

const form = ref({ name: '', email: '', subject: '', message: '' })
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
    })
    formSuccess.value = true
    form.value = { name: '', email: '', subject: '', message: '' }
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

.contact-layout { display: grid; gap: 2rem; align-items: start; }

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
  font-size: 0.85rem;
}

.form-field input,
.form-field textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--cds-border-strong);
  border-radius: 0.5rem;
  font-size: 1rem;
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

.form-field textarea { resize: vertical; min-height: 120px; }

.form-msg {
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-size: var(--cds-text-sm);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-msg-error  { background: #fff0f0; color: #c0392b; border: 1px solid #f5c6cb; }
.form-msg-success { background: #f0fff4; color: var(--cds-success); border: 1px solid #c3e6cb; }

.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 48px;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.55rem;
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-submit:disabled { opacity: 0.65; cursor: not-allowed; }

.contact-card {
  background: var(--cds-white);
  border: 1px solid var(--cds-border-soft);
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  width: 98.15%;
}

.contact-card p {
  margin: 10.05px;
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
  border-top: 4px solid var(--cds-border-soft);
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
  border-radius: 0.75rem;
  overflow: hidden;
  height: 300px;
  box-shadow: 0 4px 14px rgba(62, 60, 56, 0.12);
}

.contact-map iframe {
  width: 98%;
  height: 100%;
  border: none;
  display: block;
}

@media (min-width: 900px) {
  .contact-layout { grid-template-columns: 1fr 1fr; }
}
</style>
