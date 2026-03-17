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
        <p class="footer-brand-tagline">
          Reparación, restauración y modificación
          de sintetizadores, teclados y más.
        </p>
        <p class="footer-brand-summary">
          Agenda revisión, cotiza tu instrumento y consulta calculadoras técnicas.
        </p>
      </section>

      <section>
        <h2>Servicios</h2>
        <div class="site-footer-links">
          <router-link to="/cotizador">Cotizador</router-link>
          <router-link to="/calculadoras">Calculadoras</router-link>
          <a href="#services">Modificaciones</a>
          <a href="#services">Mantención preventiva</a>
          <a href="#services">Reparación y restauración</a>
        </div>
      </section>

      <section>
        <h2>Redes</h2>
        <div class="site-footer-links">
          <a href="https://www.instagram.com/cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer">
            <i class="fa-brands fa-instagram"></i> Instagram
          </a>
          <a href="https://www.facebook.com/Cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer">
            <i class="fa-brands fa-facebook"></i> Facebook
          </a>
          <a href="https://wa.me/56982957538" target="_blank" rel="noopener noreferrer">
            <i class="fa-brands fa-whatsapp"></i> WhatsApp
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
      <router-link to="/privacidad">Política de privacidad</router-link>
      <span>·</span>
      <router-link to="/terminos">Términos y condiciones</router-link>
      <span>·</span>
      <a href="https://github.com/CristobalZurita/cirujano-front" target="_blank" rel="noopener noreferrer">
        Repositorio
      </a>
    </div>
  </footer>
</template>

<script setup>
defineProps({
  logoSrc: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.site-footer {
  background: var(--cds-footer-bg-highlight-color);
  color: var(--cds-white);
  --footer-safe-left: clamp(1rem, 12vw, calc(1rem + 50px + 0.75rem));
  --footer-safe-right: clamp(1rem, 12vw, calc(1rem + 46px + 0.75rem));
  padding-top: clamp(3rem, 3vw, 4rem);
  padding-right: var(--footer-safe-right);
  padding-bottom: clamp(1.4rem, 1.8vw, 2rem);
  padding-left: var(--footer-safe-left);
}

.site-footer-grid {
  width: min(100%, var(--cds-content-max));
  margin-inline: auto;
  display: grid;
  gap: clamp(2rem, 2.2vw, 2.8rem);
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 13.5rem), 1fr));
  align-items: start;
}

.site-footer-grid > section {
  min-width: 0;
}

.site-footer h2 {
  margin: 0 0 0.75rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: color-mix(in srgb, var(--cds-white) 60%, transparent);
}

.site-footer p {
  margin: 0;
  font-size: var(--cds-text-sm);
  line-height: var(--cds-leading-normal);
  color: color-mix(in srgb, var(--cds-white) 75%, transparent);
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.footer-logo {
  width: clamp(96px, 12vw, 130px);
  height: clamp(96px, 12vw, 130px);
  border-radius: var(--cds-radius-sm);
}

.footer-brand .footer-brand-name {
  font-size: var(--cds-text-xl);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-white);
  margin: 0;
  line-height: 1.2;
}

.footer-brand .footer-brand-tagline {
  font-size: var(--cds-text-base);
  color: color-mix(in srgb, var(--cds-white) 65%, transparent);
  line-height: 1.5;
}

.footer-brand .footer-brand-summary {
  font-size: var(--cds-text-sm);
  color: color-mix(in srgb, var(--cds-white) 72%, transparent);
  line-height: 1.45;
  margin: 0;
}

.site-footer-links {
  display: grid;
  gap: 0.5rem;
}

.site-footer a {
  color: color-mix(in srgb, var(--cds-white) 75%, transparent);
  font-size: var(--cds-text-sm);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  transition: color 0.15s;
}

.site-footer a:hover {
  color: var(--cds-white);
}

.site-footer-links span {
  color: color-mix(in srgb, var(--cds-white) 65%, transparent);
  font-size: var(--cds-text-sm);
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.footer-map-column {
  display: flex;
  justify-content: stretch;
  align-items: flex-start;
}

.footer-map-wrap {
  display: grid;
  gap: 0.45rem;
  width: min(100%, 18rem);
  justify-items: stretch;
}

.footer-map {
  width: 100%;
  aspect-ratio: 16 / 9;
  border: 1px solid color-mix(in srgb, var(--cds-white) 18%, transparent);
  border-radius: var(--cds-radius-md);
  background: rgba(10, 10, 10, 0.25);
}

.site-footer-legal {
  width: min(100%, var(--cds-content-max));
  margin: clamp(2rem, 2.3vw, 2.8rem) auto 0;
  padding-top: 1.2rem;
  border-top: 1px solid color-mix(in srgb, var(--cds-white) 12%, transparent);
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.7rem;
  align-items: center;
  text-align: center;
  font-size: var(--cds-text-xs);
  color: color-mix(in srgb, var(--cds-white) 50%, transparent);
}

.site-footer-legal a {
  color: color-mix(in srgb, var(--cds-white) 50%, transparent);
  font-size: inherit;
}

.footer-credit {
  color: color-mix(in srgb, var(--cds-white) 62%, transparent);
}

.site-footer-legal a:hover {
  color: var(--cds-white);
}

@media (min-width: 600px) {
  .site-footer-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 960px) {
  .site-footer-grid {
    grid-template-columns: minmax(0, 1.25fr) repeat(3, minmax(0, 0.9fr)) minmax(14rem, 1fr);
  }

  .footer-map-column {
    justify-content: flex-end;
  }
}

@media (min-width: 768px) {
  .site-footer {
    --footer-safe-left: clamp(1.5rem, 8vw, calc(1.5rem + 54px + 0.9rem));
    --footer-safe-right: clamp(1.5rem, 8vw, calc(1.5rem + 50px + 0.9rem));
  }
}

@media (min-width: 1024px) {
  .site-footer-grid {
    grid-template-columns: 2fr repeat(3, minmax(0, 1fr)) minmax(250px, 265px);
    align-items: start;
  }
}
</style>
