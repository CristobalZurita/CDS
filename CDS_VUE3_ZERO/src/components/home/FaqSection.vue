<template>
  <section id="faq" class="home-section home-faq">
    <div class="section-inner container">
      <h2 class="section-title">Preguntas Frecuentes</h2>
      <p class="section-lead">Todo lo que necesitás saber sobre el taller, los tiempos, garantías y condiciones del servicio.</p>

      <div class="faq-cards">
        <button class="faq-card" @click="openModal('faq')">
          <div class="faq-card-icon">
            <i class="fas fa-circle-question"></i>
          </div>
          <div class="faq-card-body">
            <h3 class="faq-card-title">Preguntas frecuentes</h3>
            <p class="faq-card-desc">Tiempos, costos, equipos que aceptamos, garantías y cómo funciona el proceso.</p>
          </div>
          <i class="fas fa-chevron-right faq-card-arrow"></i>
        </button>

        <button class="faq-card" @click="openModal('terms')">
          <div class="faq-card-icon">
            <i class="fas fa-file-lines"></i>
          </div>
          <div class="faq-card-body">
            <h3 class="faq-card-title">Términos y condiciones</h3>
            <p class="faq-card-desc">Condiciones del servicio, bodegaje, métodos de pago y responsabilidades.</p>
          </div>
          <i class="fas fa-chevron-right faq-card-arrow"></i>
        </button>

        <button class="faq-card" @click="openModal('privacy')">
          <div class="faq-card-icon">
            <i class="fas fa-shield-halved"></i>
          </div>
          <div class="faq-card-body">
            <h3 class="faq-card-title">Política de privacidad</h3>
            <p class="faq-card-desc">Cómo recopilamos, usamos y protegemos tus datos personales.</p>
          </div>
          <i class="fas fa-chevron-right faq-card-arrow"></i>
        </button>
      </div>
    </div>

    <BaseModal v-model="modalOpen">
          <template v-if="modalContent === 'faq'">
            <div class="modal-legal-content">
              <h2>Preguntas Frecuentes</h2>
              <div class="modal-legal-scroll">
                <ul class="faq-modal-list" role="list">
                  <li
                    v-for="(faq, i) in faqs"
                    :key="faq.q"
                    class="faq-modal-item"
                    :class="{ 'is-open': openIndex === i }"
                  >
                    <button
                      class="faq-modal-question"
                      :aria-expanded="String(openIndex === i)"
                      @click="toggle(i)"
                    >
                      <span>{{ faq.q }}</span>
                      <i class="fas fa-chevron-down faq-modal-chevron" aria-hidden="true"></i>
                    </button>
                    <div class="faq-modal-body">
                      <div class="faq-modal-body-inner">
                        <p class="faq-modal-answer">{{ faq.a }}</p>
                      </div>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </template>
          <template v-else-if="modalContent === 'terms'">
            <div class="modal-legal-content">
              <h2>Términos y Condiciones</h2>
              <div class="modal-legal-scroll">
                <!-- ...contenido legal igual que antes... -->
                <section class="terms-section">
                  <h3>1. Aceptación de los Términos</h3>
                  <p>Al acceder y utilizar los servicios de Cirujano de Sintetizadores (incluyendo nuestro sitio web, aplicación, y servicios de reparación), usted acepta estar vinculado por estos Términos y Condiciones. Si no está de acuerdo con alguno de estos términos, le pedimos que no utilice nuestros servicios.</p>
                </section>
                <section class="terms-section">
                  <h3>2. Descripción de Servicios</h3>
                  <p>Cirujano de Sintetizadores ofrece servicios profesionales de reparación y mantenimiento de instrumentos musicales electrónicos, incluyendo:</p>
                  <ul>
                    <li>Cotizaciones y presupuestos estimados</li>
                    <li>Diagnóstico técnico completo</li>
                    <li>Reparación y mantenimiento</li>
                    <li>Seguimiento en línea del estado de reparación</li>
                    <li>Servicios adicionales como streaming en vivo de reparaciones</li>
                  </ul>
                </section>
                <section class="terms-section">
                  <h3>3. Cotizaciones y Presupuestos</h3>
                  <ul>
                    <li><strong>Indicativas y no vinculantes:</strong> El precio final se confirma tras revisión presencial.</li>
                    <li><strong>Presupuesto formal:</strong> $20.000 CLP, abonable si se realiza la reparación, no reembolsable si se rechaza.</li>
                    <li><strong>Validez:</strong> 30 días desde emisión.</li>
                  </ul>
                </section>
                <section class="terms-section">
                  <h3>4. Bodegaje</h3>
                  <ul>
                    <li>Primeros 30 días: gratis</li>
                    <li>Días 31-60: $5.000 CLP/mes</li>
                    <li>Día 91+: equipo considerado abandonado</li>
                  </ul>
                </section>
                <section class="terms-section">
                  <h3>5. Métodos de Pago</h3>
                  <ul>
                    <li>Tarjetas (Flow.cl)</li>
                    <li>Transferencia bancaria</li>
                    <li>Efectivo (retiro presencial)</li>
                  </ul>
                </section>
                <section class="terms-section">
                  <h3>6. Garantía de Reparación</h3>
                  <p>30 días desde entrega. No cubre mal uso, daños externos, ni componentes no disponibles.</p>
                </section>
                <section class="terms-section">
                  <h3>7. Responsabilidades del Cliente</h3>
                  <ul>
                    <li>Proveer información precisa</li>
                    <li>Retirar equipo en plazo</li>
                    <li>Abonar costos acordados</li>
                  </ul>
                </section>
                <section class="terms-section">
                  <h3>8. Limitación de Responsabilidad</h3>
                  <ul>
                    <li>Daño en transporte externo</li>
                    <li>Pérdida de datos</li>
                    <li>Daño por terceros</li>
                    <li>Reparaciones fallidas por falta de repuestos</li>
                  </ul>
                </section>
                <section class="terms-section">
                  <h3>9. Cambios</h3>
                  <p>Los términos pueden cambiar y se publican en el sitio web.</p>
                </section>
                <section class="terms-section">
                  <h3>10. Contacto</h3>
                  <ul>
                    <li>Email: info@cirujanodesintetizadores.cl</li>
                    <li>Teléfono: +56 9 XXXX XXXX</li>
                    <li>Dirección: [Tu dirección de taller]</li>
                  </ul>
                </section>
              </div>
            </div>
          </template>
          <template v-else-if="modalContent === 'privacy'">
            <div class="modal-legal-content">
              <h2>Política de Privacidad</h2>
              <div class="modal-legal-scroll">
                <!-- ...contenido legal igual que antes... -->
                <section class="privacy-section">
                  <h3>1. Introducción</h3>
                  <p>Cirujano de Sintetizadores respeta su privacidad y se compromete a proteger sus datos personales. Esta política explica cómo recopilamos, usamos y protegemos su información.</p>
                </section>
                <section class="privacy-section">
                  <h3>2. Información que Recopilamos</h3>
                  <ul>
                    <li>Nombre, email, teléfono, dirección</li>
                    <li>Identificación para facturas y contratos</li>
                    <li>Datos de pago (Flow.cl)</li>
                    <li>Marca, modelo, año, descripción de fallas, fotos, historial</li>
                    <li>IP, navegador, sistema operativo, páginas visitadas, cookies</li>
                  </ul>
                </section>
                <section class="privacy-section">
                  <h3>3. Uso de la Información</h3>
                  <ul>
                    <li>Procesar cotizaciones y reparaciones</li>
                    <li>Enviar notificaciones</li>
                    <li>Procesar pagos</li>
                    <li>Cumplir obligaciones legales</li>
                    <li>Mejorar servicios</li>
                    <li>Comunicaciones promocionales (con consentimiento)</li>
                  </ul>
                </section>
                <section class="privacy-section">
                  <h3>4. Protección de Datos</h3>
                  <ul>
                    <li>Encriptación SSL/TLS</li>
                    <li>Contraseñas hasheadas</li>
                    <li>Rate limiting y validación</li>
                    <li>Auditoría de eventos</li>
                    <li>Servidores seguros</li>
                  </ul>
                </section>
                <section class="privacy-section">
                  <h3>5. Compartir Información</h3>
                  <ul>
                    <li>Proveedores de servicios (Flow, SendGrid, Twilio)</li>
                    <li>Requisitos legales</li>
                    <li>Consentimiento explícito</li>
                  </ul>
                </section>
                <section class="privacy-section">
                  <h3>6. Cookies y Seguimiento</h3>
                  <ul>
                    <li>Mantener sesión activa</li>
                    <li>Recordar preferencias</li>
                    <li>Analítica (Google Analytics)</li>
                  </ul>
                </section>
                <section class="privacy-section">
                  <h3>7. Sus Derechos</h3>
                  <ul>
                    <li>Acceso, rectificación, eliminación, portabilidad, oposición</li>
                  </ul>
                  <p>Para ejercer derechos: info@cirujanodesintetizadores.cl</p>
                </section>
                <section class="privacy-section">
                  <h3>8. Retención de Datos</h3>
                  <ul>
                    <li>Cuenta: mientras esté activa</li>
                    <li>Reparaciones: mínimo 5 años</li>
                    <li>Pagos: según requisitos fiscales</li>
                    <li>Logs técnicos: máximo 30 días</li>
                  </ul>
                </section>
                <section class="privacy-section">
                  <h3>9. Privacidad de Menores</h3>
                  <p>No dirigido a menores de 18 años. Si se detecta, se elimina la información.</p>
                </section>
                <section class="privacy-section">
                  <h3>10. Cambios</h3>
                  <p>Podemos actualizar la política. El uso continuado implica aceptación.</p>
                </section>
                <section class="privacy-section">
                  <h3>11. Contacto</h3>
                  <ul>
                    <li>Email: privacidad@cirujanodesintetizadores.cl</li>
                    <li>Teléfono: +56 9 XXXX XXXX</li>
                    <li>Dirección: [Tu dirección de taller]</li>
                  </ul>
                </section>
              </div>
            </div>
          </template>
    </BaseModal>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'

const modalOpen = ref(false)
const modalContent = ref('')
function openModal(type) {
  modalContent.value = type
  modalOpen.value = true
}

const openIndex = ref(null)
function toggle(i) {
  openIndex.value = openIndex.value === i ? null : i
}

const faqs = [
  { q: '¿Qué tipos de equipos reparan?',         a: 'Sintetizadores analógicos y digitales, drum machines, samplers, teclados y procesadores de efectos de todas las marcas y épocas.' },
  { q: '¿Cuánto demora una reparación?',          a: 'Una revisión básica puede tardar 3-7 días hábiles. Reparaciones mayores o con espera de repuestos pueden tomar más tiempo. Siempre informamos antes de comenzar.' },
  { q: '¿Puedo traer mi equipo sin cita previa?', a: 'Recomendamos agendar antes para garantizar atención. Podés usar el sistema de citas online o contactarnos por WhatsApp.' },
  { q: '¿Tienen garantía los trabajos realizados?', a: 'Sí. Todos los trabajos tienen garantía de 90 días sobre la reparación específica realizada.' },
  { q: '¿Trabajan con equipos vintage?',           a: 'Absolutamente. Tenemos amplia experiencia con instrumentos clásicos de los años 70-90: Moog, Roland, Korg, Yamaha, Sequential, entre otros.' },
]
</script>

<style scoped src="./homeShared.css"></style>

<style scoped>
.home-faq {
  background: var(--cds-background-color);
}

/* ── Cards de entrada ─────────────────────────────────────── */
.faq-cards {
  display: grid;
  gap: var(--cds-space-sm);
}

.faq-card {
  display: flex;
  align-items: center;
  gap: var(--cds-space-lg);
  width: 100%;
  padding: var(--cds-space-lg);
  background: var(--cds-surface-1);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-lg);
  box-shadow: var(--cds-shadow-sm);
  cursor: pointer;
  text-align: left;
  transition: box-shadow 0.2s, transform 0.15s;
}

.faq-card:hover {
  box-shadow: var(--cds-shadow-md);
  transform: translateY(-1px);
}

.faq-card:focus-visible {
  outline: none;
  box-shadow: var(--cds-focus-ring);
}

.faq-card-icon {
  flex-shrink: 0;
  width: 3.2rem;
  height: 3.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--cds-radius-pill);
  font-size: 1.4rem;
  color: var(--cds-primary);
  background: var(--cds-white);
  border: 1px solid var(--cds-border-card);
}

.faq-card-body {
  flex: 1;
  min-width: 0;
  display: grid;
  gap: var(--cds-space-2xs);
}

.faq-card-title {
  margin: 0;
  font-size: var(--layout-home-text-card-title, clamp(1rem, 0.95rem + 0.28vw, 1.18rem));
  font-family: var(--layout-home-font-family-heading, var(--cds-headings-font-family), sans-serif);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-dark);
  line-height: 1.2;
  letter-spacing: -0.01em;
}

.faq-card-desc {
  margin: 0;
  font-size: clamp(0.88rem, 0.84rem + 0.18vw, 0.97rem);
  color: var(--cds-text-muted);
  line-height: 1.5;
}

.faq-card-arrow {
  flex-shrink: 0;
  font-size: 0.85rem;
  color: var(--cds-primary);
  opacity: 0.6;
  transition: transform 0.18s, opacity 0.18s;
}

.faq-card:hover .faq-card-arrow {
  transform: translateX(3px);
  opacity: 1;
}

@media (min-width: 640px) {
  .faq-cards {
    grid-template-columns: repeat(3, 1fr);
    align-items: stretch;
  }

  .faq-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .faq-card-arrow {
    display: none;
  }
}

/* ── Acordeón dentro del modal FAQ ───────────────────────── */
.faq-modal-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--cds-space-xs);
}

.faq-modal-item {
  border: 1px solid var(--cds-border-soft);
  border-radius: var(--cds-radius-md);
  background: var(--cds-surface-1);
  overflow: hidden;
}

.faq-modal-question {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--cds-space-md);
  padding: var(--cds-space-sm) var(--cds-space-md);
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  font-size: clamp(0.95rem, 0.9rem + 0.22vw, 1.06rem);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-dark);
  line-height: 1.3;
  transition: color 0.18s;
}

.faq-modal-item.is-open .faq-modal-question {
  color: var(--cds-primary);
  border-bottom: 1px solid var(--cds-border-soft);
}

.faq-modal-chevron {
  flex-shrink: 0;
  font-size: 0.8em;
  color: var(--cds-primary);
  transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.faq-modal-item.is-open .faq-modal-chevron {
  transform: rotate(180deg);
}

.faq-modal-body {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.faq-modal-item.is-open .faq-modal-body {
  grid-template-rows: 1fr;
}

.faq-modal-body-inner {
  overflow: hidden;
}

.faq-modal-answer {
  margin: 0;
  padding: var(--cds-space-xs) var(--cds-space-md) var(--cds-space-sm);
  font-size: clamp(0.9rem, 0.86rem + 0.18vw, 1rem);
  line-height: 1.65;
  color: var(--cds-text-muted);
}

/* ── Modal legal compartido ──────────────────────────────── */
.modal-legal-content {
  min-width: 0;
}

.modal-legal-scroll {
  max-height: 68vh;
  overflow-y: auto;
  padding-right: var(--cds-space-xs);
}

.modal-legal-content h2 {
  margin: 0 0 var(--cds-space-lg);
  font-size: clamp(1.3rem, 1.2rem + 0.5vw, 1.7rem);
  color: var(--cds-primary);
  line-height: 1.1;
}

.modal-legal-content h3 {
  margin: var(--cds-space-lg) 0 var(--cds-space-xs);
  font-size: clamp(0.95rem, 0.9rem + 0.22vw, 1.06rem);
  color: var(--cds-dark);
}

.modal-legal-content p {
  margin: 0 0 var(--cds-space-sm);
  line-height: 1.65;
  color: var(--cds-text-muted);
}

.modal-legal-content ul {
  padding-left: var(--cds-space-lg);
  margin: 0 0 var(--cds-space-md);
}

.modal-legal-content li {
  margin-bottom: var(--cds-space-xs);
  line-height: 1.6;
  color: var(--cds-text-muted);
}
</style>
