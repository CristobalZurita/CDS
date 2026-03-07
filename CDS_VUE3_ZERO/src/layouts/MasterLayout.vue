<template>
  <div class="master-layout">
    <header class="site-header">
      <div class="site-header-inner">
        <router-link to="/" class="brand-link">Cirujano de Sintetizadores</router-link>

        <nav class="site-nav">
          <router-link to="/">Inicio</router-link>
          <router-link to="/cotizador-ia">Cotizador IA</router-link>
          <router-link to="/agendar">Agendar</router-link>
          <router-link to="/calculadoras">Calculadoras</router-link>
          <router-link to="/tienda">Tienda</router-link>
          <router-link v-if="isAuthenticated" to="/dashboard">Dashboard</router-link>
          <router-link v-else to="/login">Ingresar</router-link>
        </nav>
      </div>
    </header>

    <main class="site-body">
      <router-view />
    </main>

    <footer class="site-footer">
      <div class="site-footer-grid">
        <section>
          <h2>Sobre el taller</h2>
          <p>
            Taller especializado en reparación, restauración y modificación de
            sintetizadores, teclados y equipos de audio.
          </p>
        </section>
        <section>
          <h2>Redes</h2>
          <div class="site-footer-links">
            <a href="https://www.instagram.com/cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer">Instagram</a>
            <a href="https://www.facebook.com/Cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer">Facebook</a>
            <a href="https://wa.me/56982957538" target="_blank" rel="noopener noreferrer">WhatsApp</a>
          </div>
        </section>
        <section>
          <h2>Contacto</h2>
          <div class="site-footer-links">
            <a href="tel:+56982957538">+56 9 8295 7538</a>
            <a href="mailto:contacto@cirujanodesintetizadores.com">contacto@cirujanodesintetizadores.com</a>
          </div>
        </section>
      </div>

      <div class="site-footer-legal">
        <router-link to="/privacidad">Política de privacidad</router-link>
        <span>·</span>
        <router-link to="/terminos">Términos y condiciones</router-link>
        <span>·</span>
        <a href="https://github.com/CristobalZurita/cirujano-front" target="_blank" rel="noopener noreferrer">
          Repositorio del proyecto
        </a>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useAuth } from '@new/composables/useAuth'

const { isAuthenticated } = useAuth()
</script>

<style scoped>
.master-layout {
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr auto;
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: var(--cds-dark);
  border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 25%, var(--cds-dark));
}

.site-header-inner {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0.8rem 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  justify-content: space-between;
}

.brand-link {
  color: var(--cds-white);
  text-decoration: none;
  font-size: var(--cds-text-lg);
  font-weight: var(--cds-font-semibold);
}

.site-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.site-nav a {
  color: var(--cds-white);
  text-decoration: none;
  min-height: 40px;
  padding: 0.55rem 0.8rem;
  border-radius: 0.55rem;
  font-size: var(--cds-text-base);
  display: inline-flex;
  align-items: center;
}

.site-nav a.router-link-active {
  background: color-mix(in srgb, var(--cds-primary) 45%, black);
}

.site-body {
  min-height: 0;
}

.site-footer {
  background: color-mix(in srgb, var(--cds-dark) 96%, black);
  color: var(--cds-white);
  padding: 1rem;
}

.site-footer-grid {
  max-width: 1180px;
  margin: 0 auto;
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

.site-footer h2 {
  margin: 0 0 0.45rem;
  font-size: var(--cds-text-lg);
}

.site-footer p {
  margin: 0;
  font-size: var(--cds-text-base);
  line-height: var(--cds-leading-normal);
}

.site-footer-links {
  display: grid;
  gap: 0.3rem;
}

.site-footer a {
  color: var(--cds-white);
  font-size: var(--cds-text-base);
}

.site-footer-legal {
  max-width: 1180px;
  margin: 1rem auto 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
  font-size: var(--cds-text-sm);
}

@media (min-width: 900px) {
  .site-footer-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
