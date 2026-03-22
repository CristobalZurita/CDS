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
  display: flex;
  flex-direction: column;
  width: 100%;
  background-color: var(--cds-dark);
}

.sim-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 100%;
}

.sim-note {
  display: none;
  margin: 0;
  padding: 0.7rem 0.9rem;
  background: rgba(236, 107, 0, 0.08);
  color: var(--cds-light);
  font-size: var(--cds-text-sm);
  line-height: 1.45;
  border-bottom: 1px solid rgba(236, 107, 0, 0.2);
  flex-shrink: 0;
}

.sim-frame-wrap {
  flex: 1;
  overflow: hidden;
  background: var(--cds-dark);
}

.sim-frame {
  width: 100%;
  height: calc(96.2dvh - var(--cds-navbar-height, 64px));
  min-height: 700px;
  border: 0;
  display: block;
}

@media (max-width: 1024px) {
  .sim-note {
    display: block;
  }

  .sim-frame {
    height: calc(100dvh - var(--cds-navbar-height, 64px) - 2.5rem);
    min-height: 78dvh;
  }
}
</style>
