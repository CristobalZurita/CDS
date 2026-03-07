<template>
  <main class="calculators-page">
    <section class="calculators-container">
      <header class="calculators-header">
        <h1>{{ title }}</h1>
        <p>{{ subtitle }}</p>
      </header>

      <div class="calculators-grid">
        <router-link
          v-for="item in calculatorItems"
          :key="item.path"
          :to="item.path"
          class="calculator-card"
        >
          <div class="calculator-card-icon">
            <i :class="item.icon"></i>
          </div>
          <div class="calculator-card-content">
            <h2>{{ item.label }}</h2>
            <p>{{ item.description }}</p>
          </div>
        </router-link>
      </div>

      <div class="calculators-actions">
        <router-link to="/" class="back-link">Volver al inicio</router-link>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useCalculatorsPage } from '@new/composables/useCalculatorsPage'

const { title, subtitle, calculatorItems } = useCalculatorsPage()
</script>

<style scoped>
.calculators-page {
  padding: 1rem;
}

.calculators-container {
  max-width: 1040px;
  margin: 0 auto;
}

.calculators-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
  line-height: var(--cds-leading-tight);
}

.calculators-header p {
  margin-top: 0.4rem;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-base);
}

.calculators-grid {
  margin-top: 1rem;
  display: grid;
  gap: 0.75rem;
  grid-template-columns: 1fr;
}

.calculator-card {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.75rem;
  padding: 0.95rem;
  border-radius: 0.8rem;
  background: var(--cds-white);
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  text-decoration: none;
  color: inherit;
}

.calculator-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 0.6rem;
  display: grid;
  place-items: center;
  background: color-mix(in srgb, var(--cds-primary) 16%, white);
  color: var(--cds-primary);
}

.calculator-card-content h2 {
  margin: 0;
  font-size: var(--cds-text-lg);
}

.calculator-card-content p {
  margin: 0.25rem 0 0;
  font-size: var(--cds-text-base);
  line-height: var(--cds-leading-normal);
}

.calculators-actions {
  margin-top: 1rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.65rem 1rem;
  border-radius: 0.6rem;
  border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white);
  color: var(--cds-primary);
  text-decoration: none;
  font-size: var(--cds-text-base);
}

@media (min-width: 768px) {
  .calculators-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
