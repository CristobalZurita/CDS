<template>
  <footer class="site-footer">
    <div class="site-footer-grid">
      <section class="footer-brand">
        <img
          :src="logoSrc"
          alt="Cirujano de Sintetizadores"
          class="footer-logo"
          width="56"
          height="56"
        />
        <p class="footer-brand-name">Cirujano de Sintetizadores</p>
    
      </section>

      <section>
        <h2>Servicios</h2>
        <div class="site-footer-links">
          <router-link to="/cotizador">Cotiza</router-link>
          <router-link to="/calculadoras">Calcula</router-link>
          <a href="#services">Modifica tus Máquinas</a>
          <router-link to="/agendar">Agenda tu revisión</router-link>
        </div>
      </section>

      <section class="footer-redes">
        <h2>Redes</h2>
        <div class="site-footer-links footer-redes-grid">
          <a href="https://www.instagram.com/cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer">
            <i class="fa-brands fa-instagram"></i> Instagram
          </a>
          <a href="https://www.facebook.com/Cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer">
            <i class="fa-brands fa-facebook"></i> Facebook
          </a>
          <a href="https://wa.me/56982957538" target="_blank" rel="noopener noreferrer">
            <i class="fa-brands fa-whatsapp"></i> WhatsApp
          </a>
          <a href="https://www.youtube.com/channel/UCijs35uOWNzQqjuoW9rmb_Q" target="_blank" rel="noopener noreferrer">
            <i class="fa-brands fa-youtube"></i> YouTube
          </a>
          <a href="https://www.tiktok.com/@cirujano.de.sinte" target="_blank" rel="noopener noreferrer">
            <i class="fa-brands fa-tiktok"></i> TikTok
          </a>
          <a href="https://x.com/Cirujano_Sintes" target="_blank" rel="noopener noreferrer">
            <i class="fa-brands fa-x-twitter"></i> X
          </a>
        </div>
      </section>

      <section>
        <h2>Contacto</h2>
        <div class="site-footer-links">
          <span><i class="fas fa-location-dot"></i> Valparaíso, Chile</span>
          <a href="tel:+56982957538">
            <i class="fas fa-phone"></i> +56 9 8295 7538
          </a>
          <a href="mailto:contacto@cirujanodesintetizadores.com">
            <i class="fas fa-envelope"></i> contacto@cirujanodesintetizadores.com
          </a>
        </div>
      </section>

      <section class="footer-map-column">
        <div class="footer-map-wrap">
          <iframe
            class="footer-map"
            title="Mapa de ubicación Cirujano de Sintetizadores"
            src="https://www.google.com/maps?q=Valpara%C3%ADso%2C%20Chile&z=13&output=embed"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
            allowfullscreen
          ></iframe>
        </div>
      </section>
    </div>



    <div class="site-footer-legal">
      <span>© 2026 Cirujano de Sintetizadores</span>
      <span>·</span>
      <span class="footer-credit">Sitio hecho por Cristobal Zurita Quintanilla · Valparaíso, Chile</span>
      <span>·</span>
      <button class="footer-legal-btn" @click="openModal('privacy')">Política de privacidad</button>
      <span>·</span>
      <button class="footer-legal-btn" @click="openModal('terms')">Términos y condiciones</button>
          <BaseModal :model-value="modalOpen" @update:model-value="modalOpen = $event">
            <template v-if="modalContent === 'terms'">
              <div class="modal-legal-content">
                <h2>Términos y Condiciones</h2>
                <div class="modal-legal-scroll">
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
      <span>·</span>
      <a href="https://github.com/CristobalZurita/cirujano-front" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
        <i class="fa-brands fa-github"></i>
      </a>
      <a href="https://www.linkedin.com/in/crist%C3%B3bal-nicol%C3%A1s-zurita-quintanilla-baa320115/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
        <i class="fa-brands fa-linkedin"></i>
      </a>
    </div>
  </footer>
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
defineProps({
  logoSrc: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.footer-legal-btn {
  background: none;
  border: none;
  color: var(--layout-public-footer-legal);
  font-size: inherit;
  cursor: pointer;
  text-decoration: underline;
  padding: 0 0.2em;
}
.footer-legal-btn:hover {
  color: var(--cds-white);
}
.modal-legal-content {
  max-width: 36rem;
}
.modal-legal-scroll {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 0.5rem;
}
.modal-legal-content h2 {
  font-size: 1.5rem;
  margin-bottom: 1.1rem;
  color: var(--cds-primary);
}
.modal-legal-content ul {
  padding-left: 1.1rem;
  margin-bottom: 1.2rem;
}
.modal-legal-content li {
  margin-bottom: 0.7rem;
}
.site-footer {
  background: var(--cds-footer-bg-color);
  color: var(--cds-white);
  font-family: var(--layout-public-font-family-base, var(--cds-font-family-base), sans-serif);
  padding-top: var(--layout-footer-padding-top, clamp(3rem, 3vw, 4rem));
  padding-right: var(--layout-footer-padding-inline, clamp(0.75rem, 2vw, 1.5rem));
  padding-bottom: var(--layout-footer-padding-bottom, clamp(1.4rem, 1.8vw, 2rem));
  padding-left: var(--layout-footer-padding-inline, clamp(0.75rem, 2vw, 1.5rem));
}

.site-footer-grid {
  width: 100%;
  max-width: none;
  margin-inline: auto;
  display: grid;
  row-gap: var(--layout-footer-grid-row-gap, clamp(2rem, 2.2vw, 2.8rem));
  column-gap: var(--layout-footer-grid-column-gap, clamp(2.4rem, 3vw, 4rem));
  grid-template-columns: var(--layout-footer-grid-template-columns, repeat(auto-fit, minmax(min(100%, 13.5rem), 1fr)));
  align-items: start;
}

.site-footer-grid > section {
  min-width: 0;
}

.site-footer h2 {
  margin: 0 0 0.75rem;
  font-family: var(--layout-public-font-family-heading, var(--layout-public-font-family-base, var(--cds-font-family-base)));
  font-size: var(--layout-public-text-label, var(--cds-text-sm));
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--layout-public-footer-heading);
}

.site-footer p {
  margin: 0;
  font-size: var(--layout-public-text-body, var(--cds-text-sm));
  line-height: 1.68;
  color: var(--layout-public-footer-text);
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  align-items: center;
  justify-self: center;
  width: var(--layout-footer-brand-width, min(100%, 16rem));
  text-align: center;
}

.footer-brand-tagline {
  margin: 0.35rem 0 0;
  font-size: var(--layout-public-text-body, var(--cds-text-sm));
  color: var(--layout-public-footer-text);
  line-height: 1.55;
  text-align: center;
  text-wrap: balance;
}

.footer-brand-summary {
  width: 100%;
  margin: var(--layout-footer-brand-summary-margin-top, clamp(1.5rem, 2vw, 2.2rem)) auto 0;
  padding: 0.2rem 0.75rem 0;
  text-align: center;
  font-size: var(--cds-text-xl);
  color: var(--layout-public-footer-text-soft);
  line-height: 1.5;
  text-wrap: balance;
}

.footer-logo {
  width: var(--layout-footer-logo-size, clamp(96px, 12vw, 130px));
  height: var(--layout-footer-logo-size, clamp(96px, 12vw, 130px));
  border-radius: var(--cds-radius-sm);
}

.footer-brand .footer-brand-name {
  font-family: var(--layout-public-font-family-heading, var(--layout-public-font-family-base, var(--cds-font-family-base)));
  font-size: var(--layout-public-text-footer-brand, var(--cds-text-xl));
  font-weight: var(--cds-font-semibold);
  color: var(--cds-white);
  margin: 0;
  line-height: 1.05;
  letter-spacing: -0.01em;
}

.site-footer-links {
  display: grid;
  gap: 0.58rem;
}

.footer-redes h2 {
  text-align: center;
  margin-right: 20px;
}

.footer-redes-grid {
  grid-template-rows: repeat(3, auto);
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  gap: 0.58rem 1rem;
  
}

.site-footer a {
  color: var(--layout-public-footer-text);
  font-size: var(--layout-public-text-body, var(--cds-text-sm));
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  line-height: 1.6;
  transition: color 0.15s;
}

.site-footer a:hover {
  color: var(--cds-white);
}

.site-footer-links span {
  color: var(--layout-public-footer-text-soft);
  font-size: var(--layout-public-text-body, var(--cds-text-sm));
  display: inline-flex;
  align-items: center;
  gap: .45rem;
  line-height: 1.6;
}

.footer-map-column {
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.footer-map-wrap {
  display: grid;
  gap: 0.45rem;
  width: 100%;
  max-width: var(--layout-footer-map-max-width, 18rem);
  justify-items: stretch;
  margin-right: var(--layout-footer-map-offset-inline, 70px);
}

.footer-map {
  width: 90%;
  aspect-ratio: 16 / 9;
  border: 1px solid rgba(203, 194, 183, 0.22);
  border-radius: var(--cds-radius-md);
  background: var(--cds-footer-bg-highlight-color);
    margin-left: 35px;
}

.site-footer-legal {
  width: 100%;
  max-width: none;
  margin: var(--layout-footer-legal-margin-top, clamp(2rem, 2.3vw, 2.8rem)) auto 0;
  padding-top: 1.2rem;
  border-top: 1px solid rgba(203, 194, 183, 0.16);
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.7rem;
  align-items: center;
  text-align: center;
  font-size: var(--layout-public-text-meta, var(--cds-text-xs));
  line-height: 1.55;
  color: var(--layout-public-footer-legal);
}

.site-footer-legal a {
  color: var(--layout-public-footer-legal);
  font-size: inherit;
}

.footer-credit {
  color: var(--layout-public-footer-text-soft);
}

.site-footer-legal a:hover {
  color: var(--cds-white);
}

@media (min-width: 600px) {
  .site-footer {
    --layout-footer-grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 960px) {
  .site-footer {
    --layout-footer-grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 1280px) {
  .site-footer {
    --layout-footer-grid-template-columns:
      minmax(15rem, 1.15fr)
      minmax(11rem, 0.9fr)
      minmax(11rem, 0.9fr)
      minmax(14rem, 1.05fr)
      minmax(18rem, 1.1fr);
  }

  .footer-map-column {
    justify-content: center;
  }
}
</style>
