<template>
  <div class="privacy-page">
    <div class="privacy-container">
      <div class="privacy-header">
        <h1>Política de Privacidad</h1>
        <p class="last-updated">Última actualización: Enero 2026</p>
      </div>

      <div class="privacy-content">
        <section class="privacy-section">
          <h2>1. Introducción</h2>
          <p>
            Cirujano de Sintetizadores respeta su privacidad y se compromete a proteger
            sus datos personales. Esta Política de Privacidad explica cómo recopilamos,
            usamos y protegemos su información cuando utiliza nuestros servicios.
          </p>
        </section>

        <section class="privacy-section">
          <h2>2. Información que Recopilamos</h2>
          <h3>2.1 Información Personal</h3>
          <ul>
            <li>Nombre, email, teléfono y dirección</li>
            <li>Información de identificación para facturas y contratos</li>
            <li>Datos de pago (procesados de forma segura por Flow.cl)</li>
          </ul>

          <h3>2.2 Información de Equipos</h3>
          <ul>
            <li>Marca, modelo y año del instrumento</li>
            <li>Descripción de fallas y problemas</li>
            <li>Fotos e imágenes del equipo</li>
            <li>Historial de reparaciones previas</li>
          </ul>

          <h3>2.3 Información Técnica</h3>
          <ul>
            <li>Dirección IP, tipo de navegador, sistema operativo</li>
            <li>Páginas visitadas y tiempo de permanencia</li>
            <li>Información de cookies y identificadores similares</li>
          </ul>
        </section>

        <section class="privacy-section">
          <h2>3. Cómo Usamos su Información</h2>
          <p>Utilizamos su información para:</p>
          <ul>
            <li>Procesar cotizaciones y presupuestos</li>
            <li>Realizar reparaciones y mantenimiento</li>
            <li>Enviar notificaciones sobre el estado de su reparación</li>
            <li>Procesar pagos</li>
            <li>Cumplir con obligaciones legales y regulatorias</li>
            <li>Mejorar nuestros servicios y experiencia de usuario</li>
            <li>Enviar comunicaciones promocionales (solo con su consentimiento)</li>
          </ul>
        </section>

        <section class="privacy-section">
          <h2>4. Protección de Datos</h2>
          <p>
            Implementamos medidas de seguridad técnicas y organizacionales para proteger
            su información personal:
          </p>
          <ul>
            <li>Encriptación SSL/TLS para todas las transmisiones de datos</li>
            <li>Contraseñas hasheadas con bcrypt (nunca almacenamos contraseñas en texto plano)</li>
            <li>Rate limiting y validación de entrada para prevenir ataques</li>
            <li>Auditoría de eventos para detectar acceso no autorizado</li>
            <li>Servidores seguros con acceso restringido</li>
          </ul>
        </section>

        <section class="privacy-section">
          <h2>5. Compartir Información</h2>
          <p>No compartimos su información personal con terceros excepto:</p>
          <ul>
            <li>
              <strong>Proveedores de servicios:</strong> Solo cuando sea necesario para
              procesar pagos (Flow.cl), enviar emails (SendGrid) o SMS (Twilio)
            </li>
            <li>
              <strong>Requisitos legales:</strong> Cuando la ley nos obligue a divulgar
              información
            </li>
            <li>
              <strong>Consentimiento explícito:</strong> Si usted autoriza compartir
              información para un propósito específico
            </li>
          </ul>
        </section>

        <section class="privacy-section">
          <h2>6. Cookies y Seguimiento</h2>
          <p>Utilizamos cookies para:</p>
          <ul>
            <li>Mantener su sesión activa (sesiones técnicas)</li>
            <li>Recordar preferencias (idioma, tema)</li>
            <li>Analizar cómo usa nuestro sitio (Google Analytics)</li>
          </ul>
          <p>
            Puede controlar las cookies en la configuración de su navegador.
            Desactivar cookies puede afectar la funcionalidad del sitio.
          </p>
        </section>

        <section class="privacy-section">
          <h2>7. Sus Derechos</h2>
          <p>Tiene derecho a:</p>
          <ul>
            <li><strong>Acceso:</strong> Solicitar una copia de sus datos personales</li>
            <li><strong>Rectificación:</strong> Corregir información inexacta</li>
            <li><strong>Eliminación:</strong> Solicitar la eliminación de sus datos ("derecho al olvido")</li>
            <li><strong>Portabilidad:</strong> Recibir sus datos en formato transportable</li>
            <li><strong>Oposición:</strong> Oponerse al uso de sus datos para marketing</li>
          </ul>
          <p>Para ejercer estos derechos, contáctenos a info@cirujanodesintetizadores.cl</p>
        </section>

        <section class="privacy-section">
          <h2>8. Retención de Datos</h2>
          <p>Retenemos su información durante:</p>
          <ul>
            <li><strong>Datos de cuenta:</strong> Mientras tenga una cuenta activa</li>
            <li><strong>Registros de reparación:</strong> Mínimo 5 años (requisito legal)</li>
            <li><strong>Datos de pago:</strong> Según requisitos fiscales (7 años)</li>
            <li><strong>Logs técnicos:</strong> Máximo 30 días a menos que sea necesario para seguridad</li>
          </ul>
        </section>

        <section class="privacy-section">
          <h2>9. Privacidad de Menores</h2>
          <p>
            Nuestros servicios no están dirigidos a menores de 18 años.
            No recopilamos información de menores de 18 años conocidamente.
            Si descubrimos que hemos recopilado datos de un menor, eliminaremos
            esa información inmediatamente.
          </p>
        </section>

        <section class="privacy-section">
          <h2>10. Cambios a esta Política</h2>
          <p>
            Podemos actualizar esta Política de Privacidad ocasionalmente.
            Le notificaremos de cambios significativos por email.
            El uso continuado de nuestros servicios implica aceptación de los cambios.
          </p>
        </section>

        <section class="privacy-section last-section">
          <h2>11. Contacto</h2>
          <p>Para preguntas sobre privacidad, contáctenos a:</p>
          <ul>
            <li>Email: privacidad@cirujanodesintetizadores.cl</li>
            <li>Teléfono: +56 9 XXXX XXXX</li>
            <li>Dirección: [Tu dirección de taller]</li>
          </ul>
        </section>
      </div>

      <div class="actions">
        <router-link :to="backToTerms" class="btn-back">← Volver a Términos</router-link>
        <router-link :to="backToHome" class="btn-next">Volver a Inicio →</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { usePrivacyPage } from '@/composables/usePrivacyPage'

const { backToTerms, backToHome } = usePrivacyPage()
</script>

<style scoped src="./commonLegalPage.css"></style>

<style scoped>
.btn-back {
  color: var(--cds-primary);
  border: 1px solid color-mix(in srgb, var(--cds-primary) 40%, white);
}

.btn-next {
  border: 1px solid var(--cds-primary);
  background: var(--cds-primary);
  color: var(--cds-white);
}
</style>
