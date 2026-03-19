<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>{{ title }}</h1>
        <p v-if="description">{{ description }}</p>
      </header>
      <div class="calc-layout">
        <slot />
      </div>
      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' }
})
</script>

<style scoped>
.calc-page {
  padding: var(--layout-calculator-page-padding, var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl));
  background: var(--cds-background-color);
}

.calc-container {
  max-width: var(--layout-calculator-container-max, 1160px);
  margin: 0 auto;
  display: grid;
  gap: var(--layout-calculator-content-gap, 1.2rem);
}

.calc-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
  line-height: var(--cds-leading-tight);
}

.calc-header p {
  margin: 0.4rem 0 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-base);
}

.calc-layout {
  display: grid;
  gap: var(--layout-calculator-layout-gap, 1rem);
  grid-template-columns: 1fr;
}

@media (min-width: 920px) {
  .calc-layout {
    grid-template-columns: var(--layout-calculator-layout-columns-desktop, minmax(320px, 1fr) minmax(360px, 1.2fr));
    align-items: start;
  }
}

.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.65rem 1rem;
  border: 1px solid var(--cds-primary);
  border-radius: 0.6rem;
  text-decoration: none;
  color: var(--cds-primary);
  width: fit-content;
  font-weight: var(--cds-font-semibold);
  font-size: var(--cds-text-sm);
}
</style>
