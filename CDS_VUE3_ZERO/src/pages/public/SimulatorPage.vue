<template>
  <section class="sim-page" aria-label="Simulador de circuitos">
    <section class="sim-container">
      <p class="sim-note" role="note">
        En moviles y tabletas, este simulador corre mejor en navegador web de PC.
      </p>

      <section class="sim-frame-wrap" aria-label="Simulador Falstad embebido">
        <iframe
          class="sim-frame"
          src="https://www.falstad.com/circuit/circuitjs.html"
          title="Falstad Circuit Simulator"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
        ></iframe>
      </section>
    </section>
  </section>
</template>

<script setup>
</script>

<style scoped>
.sim-page {
  min-height: 100vh;
  padding: var(--cds-space-sm);
  background-color: var(--cds-background-color);
}

.sim-container {
  max-width: min(98vw, 1600px);
  margin: 0 auto;
}

.sim-note {
  display: none;
  margin: 0 0 var(--cds-space-sm);
  padding: 0.7rem 0.9rem;
  border: 1px solid rgba(236, 107, 0, 0.2);
  border-radius: var(--cds-radius-md);
  background: rgba(236, 107, 0, 0.08);
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  line-height: 1.45;
}

.sim-frame-wrap {
  border: 1px solid var(--cds-border-strong);
  border-radius: var(--cds-radius-md);
  overflow: hidden;
  box-shadow: var(--cds-shadow-sm);
  background: var(--cds-dark);
}

.sim-frame {
  width: 100%;
  height: calc(100vh - var(--cds-navbar-height) - 1rem);
  min-height: 700px;
  border: 0;
  display: block;
}

@media (max-width: 1024px) {
  .sim-note {
    display: block;
  }

  .sim-frame {
    height: calc(100vh - var(--cds-navbar-height) - 1rem);
    min-height: 78vh;
  }
}
</style>
