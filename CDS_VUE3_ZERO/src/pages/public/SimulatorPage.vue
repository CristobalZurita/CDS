<template>
  <section class="sim-page" aria-label="Simulador de circuitos">
    <section class="sim-container">
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

.sim-frame-wrap {
  border: 1px solid rgba(62, 60, 56, 0.28);
  border-radius: var(--cds-radius-md);
  overflow: hidden;
  box-shadow: var(--cds-shadow-sm);
  background: #111;
}

.sim-frame {
  width: 100%;
  height: calc(100vh - var(--cds-navbar-height) - 1rem);
  min-height: 700px;
  border: 0;
  display: block;
}

@media (max-width: 900px) {
  .sim-frame {
    height: calc(100vh - var(--cds-navbar-height) - 1rem);
    min-height: 78vh;
  }
}
</style>
