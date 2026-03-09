<template>
  <div class="terms-page">
    <div class="terms-container">
      <div class="terms-header">
        <h1>Términos y Condiciones</h1>
        <p class="last-updated">Última actualización: Enero 2026</p>
      </div>

      <div class="terms-content">
        <section class="terms-section">
          <h2>1. Aceptación de los Términos</h2>
          <p>
            Al acceder y utilizar los servicios de Cirujano de Sintetizadores
            (incluyendo nuestro sitio web, aplicación, y servicios de reparación),
            usted acepta estar vinculado por estos Términos y Condiciones.
            Si no está de acuerdo con alguno de estos términos, le pedimos que
            no utilice nuestros servicios.
          </p>
        </section>

        <section class="terms-section">
          <h2>2. Descripción de Servicios</h2>
          <p>
            Cirujano de Sintetizadores ofrece servicios profesionales de reparación
            y mantenimiento de instrumentos musicales electrónicos, incluyendo:
          </p>
          <ul>
            <li>Cotizaciones y presupuestos estimados</li>
            <li>Diagnóstico técnico completo</li>
            <li>Reparación y mantenimiento</li>
            <li>Seguimiento en línea del estado de reparación</li>
            <li>Servicios adicionales como streaming en vivo de reparaciones</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2>3. Cotizaciones y Presupuestos</h2>
          <h3>3.1 Naturaleza Indicativa</h3>
          <p>
            Todas las cotizaciones generadas a través de nuestra plataforma en línea
            son <strong>INDICATIVAS y NO VINCULANTES</strong>. El precio final será
            confirmado únicamente tras una revisión presencial del equipo en nuestro taller.
          </p>

          <h3>3.2 Presupuesto Formal</h3>
          <p>
            El presupuesto formal tiene un costo de <strong>$20.000 CLP</strong>, que es:
          </p>
          <ul>
            <li>
              <strong>ABONABLE:</strong> Se descuenta del total si el cliente decide
              proceder con la reparación
            </li>
            <li>
              <strong>NO REEMBOLSABLE:</strong> Si el cliente rechaza la reparación,
              esta cantidad queda como pago por el diagnóstico completo realizado
            </li>
          </ul>

          <h3>3.3 Validez de Cotizaciones</h3>
          <p>
            Las cotizaciones generadas son válidas por 30 días desde su fecha de emisión.
            Después de este período, el cliente debe solicitar una nueva cotización.
          </p>
        </section>

        <section class="terms-section">
          <h2>4. Política de Bodegaje</h2>
          <ul>
            <li>
              <strong>Primeros 30 días:</strong> Gratis. El cliente tiene este tiempo para
              retirar el equipo reparado o para contactarnos
            </li>
            <li>
              <strong>Días 31-60:</strong> $5.000 CLP por mes. El cliente debe
              abonar este monto para mantener el equipo en bodegaje
            </li>
            <li>
              <strong>Día 91 en adelante:</strong> El equipo se considera abandonado.
              Cirujano de Sintetizadores podrá disponer del equipo según lo determine
            </li>
          </ul>
        </section>

        <section class="terms-section">
          <h2>5. Métodos de Pago</h2>
          <p>
            Aceptamos los siguientes métodos de pago:
          </p>
          <ul>
            <li>Tarjetas de débito y crédito (Visa, Mastercard) a través de Flow.cl</li>
            <li>Transferencia bancaria</li>
            <li>Efectivo (solo para retiro presencial)</li>
          </ul>
          <p>
            Los pagos se procesarán de forma segura. Para cotizaciones en línea,
            el cliente debe aceptar esta política de términos antes de completar
            la transacción.
          </p>
        </section>

        <section class="terms-section">
          <h2>6. Garantía de Reparación</h2>
          <p>
            Todos nuestros trabajos de reparación incluyen una garantía de
            <strong>30 días</strong> desde la fecha de entrega, cubriendo defectos
            en la reparación realizada.
          </p>
          <p>La garantía NO cubre:</p>
          <ul>
            <li>Daño por mal uso después de la reparación</li>
            <li>Problemas causados por hardware no relacionado con la reparación</li>
            <li>Daño por exposición a humedad, calor o condiciones ambientales extremas</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2>7. Responsabilidades del Cliente</h2>
          <p>El cliente es responsable de:</p>
          <ul>
            <li>Proporcionar información precisa sobre el instrumento</li>
            <li>Retirar el equipo dentro del plazo de 30 días</li>
            <li>Abonar los costos acordados en el plazo determinado</li>
            <li>Usar el equipo reparado de conformidad con sus especificaciones</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2>8. Limitación de Responsabilidad</h2>
          <p>Cirujano de Sintetizadores no se responsabiliza por:</p>
          <ul>
            <li>Daño al equipo durante el transporte hacia o desde el taller (excepto si transportamos nosotros)</li>
            <li>Pérdida de datos o información en dispositivos de almacenamiento</li>
            <li>Daño causado por terceros o vandalismo</li>
            <li>Reparaciones fallidas debidas a componentes no disponibles en el mercado</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2>9. Cambios a estos Términos</h2>
          <p>
            Cirujano de Sintetizadores se reserva el derecho de modificar estos
            términos en cualquier momento. Los cambios serán efectivos cuando se
            publiquen en el sitio web. El uso continuado de nuestros servicios
            constituye aceptación de los términos modificados.
          </p>
        </section>

        <section class="terms-section last-section">
          <h2>10. Contacto</h2>
          <p>Para preguntas sobre estos Términos y Condiciones, contáctenos a:</p>
          <ul>
            <li>Email: info@cirujanodesintetizadores.cl</li>
            <li>Teléfono: +56 9 XXXX XXXX</li>
            <li>Dirección: [Tu dirección de taller]</li>
          </ul>
        </section>
      </div>

      <div class="acceptance-box">
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="accepted"
            class="checkbox-input"
          />
          <span>He leído y acepto los Términos y Condiciones</span>
        </label>
      </div>

      <div class="actions">
        <router-link to="/" class="btn-back">← Volver</router-link>
        <button
          @click="goToPrivacy"
          class="btn-next"
          :disabled="!canContinue"
        >
          Ver Política de Privacidad →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useTermsPage } from '@/composables/useTermsPage'

const { accepted, canContinue, goToPrivacy } = useTermsPage()
</script>

<style scoped>
.terms-page {
  padding: 1rem;
}

.terms-container {
  max-width: 980px;
  margin: 0 auto;
  background: var(--cds-white);
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 1rem;
  padding: 1rem;
}

.terms-header {
  margin-bottom: 1rem;
}

.terms-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
  line-height: var(--cds-leading-tight);
}

.last-updated {
  margin-top: 0.35rem;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.terms-content {
  display: grid;
  gap: 1rem;
}

.terms-section h2 {
  margin: 0 0 0.6rem;
  font-size: var(--cds-text-xl);
}

.terms-section h3 {
  margin: 0.8rem 0 0.4rem;
  font-size: var(--cds-text-lg);
}

.terms-section p,
.terms-section li {
  font-size: var(--cds-text-base);
  line-height: var(--cds-leading-normal);
}

.terms-section ul {
  margin: 0.35rem 0 0;
  padding-left: 1.2rem;
}

.acceptance-box {
  margin-top: 1rem;
  padding: 0.8rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--cds-light) 15%, white);
}

.checkbox-label {
  display: flex;
  align-items: start;
  gap: 0.6rem;
  font-size: var(--cds-text-base);
}

.checkbox-input {
  margin-top: 0.15rem;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.btn-back,
.btn-next {
  border-radius: 0.6rem;
  min-height: 44px;
  padding: 0.7rem 1rem;
  font-size: var(--cds-text-base);
  text-decoration: none;
}

.btn-back {
  color: var(--cds-primary);
  border: 1px solid color-mix(in srgb, var(--cds-primary) 40%, white);
}

.btn-next {
  border: 1px solid var(--cds-primary);
  background: var(--cds-primary);
  color: var(--cds-white);
}

.btn-next:disabled {
  opacity: 0.5;
}
</style>
