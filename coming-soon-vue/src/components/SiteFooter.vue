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
        <h2 class="footer-section-title">Servicios</h2>
        <div class="site-footer-links">
          <a href="#contacto" class="footer-link">Cotización</a>
          <a href="#contacto" class="footer-link">Modificaciones</a>
          <a href="#contacto" class="footer-link">Mantención preventiva</a>
          <a href="#contacto" class="footer-link">Reparación y restauración</a>
        </div>
      </section>

      <section>
        <h2 class="footer-section-title">Redes</h2>
        <div class="site-footer-links">
          <a href="https://www.instagram.com/cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer" class="footer-link">
            <i class="fa-brands fa-instagram"></i> Instagram
          </a>
          <a href="https://www.facebook.com/Cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer" class="footer-link">
            <i class="fa-brands fa-facebook"></i> Facebook
          </a>
          <a href="https://wa.me/56982957538" target="_blank" rel="noopener noreferrer" class="footer-link">
            <i class="fa-brands fa-whatsapp"></i> WhatsApp
          </a>
          <a href="https://www.youtube.com/channel/UCijs35uOWNzQqjuoW9rmb_Q" target="_blank" rel="noopener noreferrer" class="footer-link">
            <i class="fa-brands fa-youtube"></i> YouTube
          </a>
          <a href="https://www.tiktok.com/@cirujano.de.sinte" target="_blank" rel="noopener noreferrer" class="footer-link">
            <i class="fa-brands fa-tiktok"></i> TikTok
          </a>
          <a href="https://x.com/Cirujano_Sintes" target="_blank" rel="noopener noreferrer" class="footer-link">
            <i class="fa-brands fa-x-twitter"></i> X
          </a>
        </div>
      </section>

      <section>
        <h2 class="footer-section-title">Contacto</h2>
        <div class="site-footer-links">
          <span class="footer-link-span"><i class="fas fa-location-dot"></i> Valparaíso, Chile</span>
          <a href="tel:+56982957538" class="footer-link">
            <i class="fas fa-phone"></i> +56 9 8295 7538
          </a>
          <a href="mailto:cirujanodesintetizadores@gmail.com" class="footer-link">
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
      <span class="footer-legal-text">© 2026 Cirujano de Sintetizadores</span>
      <span class="footer-legal-sep">·</span>
      <span class="footer-credit">Valparaíso, Chile</span>
      <span class="footer-legal-sep">·</span>
      <a href="mailto:cirujanodesintetizadores@gmail.com" class="footer-legal-link">cirujanodesintetizadores@gmail.com</a>
      <span class="footer-legal-sep">·</span>
      <span class="footer-credit">Creado por Cristóbal Zurita Quintanilla</span>
      <a href="https://github.com/CristobalZurita" target="_blank" rel="noopener noreferrer" aria-label="GitHub" class="footer-legal-link">
        <i class="fa-brands fa-github"></i>
      </a>
      <a href="https://www.linkedin.com/in/crist%C3%B3bal-nicol%C3%A1s-zurita-quintanilla-baa320115/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn" class="footer-legal-link">
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

.footer-section-title {
  margin: 0 0 0.75rem;
  font-size: clamp(1.15rem, 1.4vw, 1.33rem);
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: color-mix(in srgb, var(--cds-white) 55%, transparent);
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.footer-logo {
  width: 100px;
  height: auto;
  border-radius: var(--cds-radius-sm);
}

.footer-brand-name {
  margin: 0;
  font-size: clamp(1.54rem, 2.8vw, 1.82rem);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-white);
  line-height: 1.2;
}

.footer-brand-tagline {
  margin: 0;
  font-size: clamp(1.65rem, 1.8vw, 1.33rem);
  line-height: 1.5;
  color: color-mix(in srgb, var(--cds-white) 60%, transparent);
}

.footer-brand-summary {
  margin: 0;
  font-size: clamp(1.66rem, 1.8vw, 1.33rem);
  line-height: 1.45;
  color: color-mix(in srgb, var(--cds-white) 65%, transparent);
}

.site-footer-links {
  display: grid;
  gap: 0.5rem;
}

.footer-link {
  color: color-mix(in srgb, var(--cds-white) 72%, transparent);
  font-size: clamp(1.26rem, 2.1vw, 1.4rem);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  transition: color 0.15s;
}

.footer-link:hover { color: var(--cds-white); }

.footer-link-span {
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
  margin-left: 14.5%;
}

.footer-map-wrap {
  display: grid;
  gap: 0.45rem;
}

.footer-map {
  width: min(300px, 100%);
  aspect-ratio: 16 / 9;
  border: 8px solid color-mix(in srgb, var(--cds-white) 15%, transparent);
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
}

.footer-legal-text {
  font-size: clamp(1.09rem, 1.68vw, 1.23rem);
  color: color-mix(in srgb, var(--cds-white) 45%, transparent);
}

.footer-legal-sep {
  font-size: clamp(1.09rem, 1.68vw, 1.23rem);
  color: color-mix(in srgb, var(--cds-white) 30%, transparent);
}

.footer-legal-link {
  font-size: clamp(1.09rem, 1.68vw, 1.23rem);
  color: color-mix(in srgb, var(--cds-white) 48%, transparent);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: color 0.15s;
}

.footer-legal-link:hover { color: var(--cds-white); }

.footer-credit {
  font-size: clamp(1.09rem, 1.68vw, 1.23rem);
  color: color-mix(in srgb, var(--cds-white) 58%, transparent);
}

@media (max-width: 599px) {
  .footer-brand          { text-align: center; align-items: center; }
  .site-footer-grid      { text-align: center; }
  .site-footer-links     { justify-items: center; }
  .footer-section-title  { font-size: 1.55rem; }
  .footer-link           { font-size: 1.70rem; }
  .footer-link-span      { font-size: 1.70rem; }
  .footer-map-column     { margin-left: 0; justify-content: center; }
}

@media (min-width: 600px) {
  .site-footer-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .site-footer-grid {
    grid-template-columns: 2fr repeat(3, minmax(0, 1fr)) minmax(230px, 260px);
    align-items: start;
  }
}
</style>
