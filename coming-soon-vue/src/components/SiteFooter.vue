<template>
  <footer class="site-footer">
    <div class="site-footer-grid">

      <section class="footer-brand">
        <img
          src="/images/logo/logo_square_004.webp"
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
          <a href="#contacto">Cotización</a>
          <a href="#contacto">Modificaciones</a>
          <a href="#contacto">Mantención preventiva</a>
          <a href="#contacto">Reparación y restauración</a>
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
          <a href="mailto:cirujanodesintetizadores@gmail.com">
            <i class="fas fa-envelope"></i> cirujanodesintetizadores@gmail.com
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
      <span class="footer-credit">Valparaíso, Chile</span>
      <span>·</span>
      <a href="mailto:cirujanodesintetizadores@gmail.com">cirujanodesintetizadores@gmail.com</a>
      <span>·</span>
      <span class="footer-credit">Creado por Cristóbal Zurita Quintanilla</span>
      <a href="https://github.com/CristobalZurita" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
        <i class="fa-brands fa-github"></i>
      </a>
      <a href="https://www.linkedin.com/in/crist%C3%B3bal-nicol%C3%A1s-zurita-quintanilla-baa320115/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
        <i class="fa-brands fa-linkedin"></i>
      </a>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  background: var(--cds-footer-bg);
  color: var(--cds-white);
  --footer-safe-left:  clamp(1rem, 6vw, 4rem);
  --footer-safe-right: clamp(1rem, 6vw, 4rem);
  padding-top:    clamp(3rem, 3vw, 4rem);
  padding-right:  var(--footer-safe-right);
  padding-bottom: clamp(1.4rem, 1.8vw, 2rem);
  padding-left:   var(--footer-safe-left);
}

.site-footer-grid {
  display: grid;
  gap: clamp(2rem, 2.2vw, 2.8rem);
  grid-template-columns: 1fr;
}

.site-footer h2 {
  margin: 0 0 0.75rem;
  font-size: clamp(1.15rem, 1.4vw, 1.33rem);
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: color-mix(in srgb, var(--cds-white) 55%, transparent);
}

.site-footer p {
  margin: 0;
  font-size: clamp(1.33rem, 2.1vw, 1.47rem);
  line-height: var(--cds-leading-normal);
  color: color-mix(in srgb, var(--cds-white) 70%, transparent);
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.footer-logo {
  width: 80px;
  height: 80px;
  border-radius: var(--cds-radius-sm);
}

.footer-brand-name {
  font-size: clamp(1.54rem, 2.8vw, 1.82rem) !important;
  font-weight: var(--cds-font-semibold);
  color: var(--cds-white) !important;
  line-height: 1.2;
}

.footer-brand-tagline {
  color: color-mix(in srgb, var(--cds-white) 60%, transparent) !important;
  line-height: 1.5;
}

.footer-brand-summary {
  color: color-mix(in srgb, var(--cds-white) 65%, transparent) !important;
  line-height: 1.45;
}

.site-footer-links {
  display: grid;
  gap: 0.5rem;
}

.site-footer a {
  color: color-mix(in srgb, var(--cds-white) 72%, transparent);
  font-size: clamp(1.26rem, 2.1vw, 1.4rem);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  transition: color 0.15s;
}

.site-footer a:hover { color: var(--cds-white); }

.site-footer-links span {
  color: color-mix(in srgb, var(--cds-white) 60%, transparent);
  font-size: clamp(1.26rem, 2.1vw, 1.4rem);
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.footer-map-column {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
}

.footer-map-wrap {
  display: grid;
  gap: 0.45rem;
}

.footer-map {
  width: min(240px, 100%);
  aspect-ratio: 16 / 9;
  border: 1px solid color-mix(in srgb, var(--cds-white) 15%, transparent);
  border-radius: var(--cds-radius-sm);
  background: color-mix(in srgb, var(--cds-dark) 80%, black);
}

.site-footer-legal {
  width: 100%;
  margin: clamp(2rem, 2.3vw, 2.8rem) 0 0;
  padding-top: 1.2rem;
  border-top: 1px solid color-mix(in srgb, var(--cds-white) 10%, transparent);
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.7rem;
  align-items: center;
  text-align: center;
  font-size: clamp(1.09rem, 1.68vw, 1.23rem);
  color: color-mix(in srgb, var(--cds-white) 45%, transparent);
}

.site-footer-legal a {
  color: color-mix(in srgb, var(--cds-white) 48%, transparent);
  font-size: inherit;
}

.site-footer-legal a:hover { color: var(--cds-white); }

.footer-credit {
  color: color-mix(in srgb, var(--cds-white) 58%, transparent);
}

@media (min-width: 600px) {
  .site-footer-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .site-footer-grid {
    grid-template-columns: 2fr repeat(3, minmax(0, 1fr)) minmax(230px, 260px);
    align-items: start;
  }

  /* En desktop reducir tamaños al rango normal de footer */
  .site-footer h2          { font-size: 0.82rem; }
  .site-footer p           { font-size: 0.95rem; }
  .footer-brand-name       { font-size: 1.15rem !important; }
  .site-footer a,
  .site-footer-links span  { font-size: 0.9rem; }
  .site-footer-legal       { font-size: 0.8rem; }
}
</style>
