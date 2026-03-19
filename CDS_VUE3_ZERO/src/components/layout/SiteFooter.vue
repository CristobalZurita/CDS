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
  padding-top: clamp(3rem, 3vw, 4rem);
  padding-right: clamp(0.75rem, 2vw, 1.5rem);
  padding-bottom: clamp(1.4rem, 1.8vw, 2rem);
  padding-left: clamp(0.75rem, 2vw, 1.5rem);
}

.site-footer-grid {
  width: 90%;
  max-width: none;
  margin-inline: auto;
  display: grid;
  row-gap: clamp(2rem, 2.2vw, 2.8rem);
  column-gap: clamp(2.4rem, 3vw, 4rem);
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 13.5rem), 1fr));
  align-items: start;
}

.site-footer-grid > section {
  min-width: 0;
    margin-right: 40px;
}

.site-footer h2 {
  margin: 0 0 0.75rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #d8d2ca;
}

.site-footer p {
  margin: 0;
  font-size: var(--cds-text-sm);
  line-height: var(--cds-leading-normal);
  color: #e4ddd4;
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  align-items: center;
  justify-self: center;
  width: min(100%, 16rem);
  text-align: center;
}

.footer-brand-summary {
  width: 100%;
  margin: clamp(1.5rem, 2vw, 2.2rem) auto 0;
  padding: 0.2rem 0.75rem 0;
  text-align: center;
  font-size: var(--cds-text-xl);
  color: #d6cec5;
  line-height: 1.5;
  text-wrap: balance;
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
  line-height: 1;
}

.site-footer-links {
  display: grid;
  gap: 0.5rem;
}

.site-footer a {
  color: #e4ddd4;
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
  color: #d6cec5;
  font-size: var(--cds-text-sm);
  display: inline-flex;
  align-items: center;
  gap: .45rem;
}

.footer-map-column {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  margin-right: 60px;
}

.footer-map-wrap {
  display: grid;
  gap: 0.45rem;
  width: 100%;
  max-width: 18rem;
  justify-items: stretch;
}

.footer-map {
  width: 100%;
  aspect-ratio: 16 / 9;
  border: 1px solid #5e5953;
  border-radius: var(--cds-radius-md);
  background: #2c2926;
}

.site-footer-legal {
  width: 100%;
  max-width: none;
  margin: clamp(2rem, 2.3vw, 2.8rem) auto 0;
  padding-top: 1.2rem;
  border-top: 1px solid #5e5953;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.7rem;
  align-items: center;
  text-align: center;
  font-size: var(--cds-text-xs);
  color: #c8c0b6;
}

.site-footer-legal a {
  color: #c8c0b6;
  font-size: inherit;
}

.footer-credit {
  color: #d4ccbf;
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
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 1280px) {
  .site-footer-grid {
    grid-template-columns:
      minmax(15rem, 1.15fr)
      minmax(11rem, 0.9fr)
      minmax(11rem, 0.9fr)
      minmax(14rem, 1.05fr)
      minmax(18rem, 1.1fr);
    align-items: start;
  }

  .footer-map-column {
    justify-content: center;
  }
}
</style>
