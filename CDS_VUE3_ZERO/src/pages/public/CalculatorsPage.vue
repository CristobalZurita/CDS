<template>
  <section class="calculators-page">
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
  </section>
</template>

<script setup>
import { useCalculatorsPage } from '@/composables/useCalculatorsPage'

const { title, subtitle, calculatorItems } = useCalculatorsPage()
</script>

<style scoped>
.calculators-page {
  min-height: 100vh;
  padding: var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl);
  background:
    radial-gradient(circle at top left, rgba(236, 107, 0, 0.12), transparent 30%),
    radial-gradient(circle at top right, rgba(3, 134, 0, 0.08), transparent 24%);
}

.calculators-container {
  max-width: var(--cds-content-max);
  margin: 0 auto;
}

.calculators-header {
  padding: var(--cds-space-xl);
  border-radius: var(--cds-radius-lg);
  background: var(--cds-surface-1);
  border: 1px solid var(--cds-border-soft);
  box-shadow: var(--cds-shadow-md);
}

.calculators-header h1 {
  margin: 0;
  font-size: clamp(2rem, 3.2vw, 3rem);
  letter-spacing: 0.03em;
  text-transform: uppercase;
  line-height: 1.1;
}

.calculators-header p {
  margin-top: var(--cds-space-xs);
  color: var(--cds-text-muted);
  font-size: 1.02rem;
}

.calculators-grid {
  margin-top: var(--cds-space-lg);
  display: grid;
  gap: var(--cds-space-md);
  grid-template-columns: 1fr;
}

.calculator-card {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  padding: 1.25rem 1.35rem;
  border-radius: var(--cds-radius-lg);
  border: 1px solid rgba(62, 60, 56, 0.14);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.88), rgba(233, 236, 230, 0.66));
  box-shadow: var(--cds-shadow-sm);
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.calculator-card:hover {
  transform: translateY(-4px);
  border-color: rgba(236, 107, 0, 0.35);
  box-shadow: var(--cds-shadow-md);
}

.calculator-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(236, 107, 0, 0.12);
  color: var(--cds-primary);
  font-size: 1.1rem;
}

.calculator-card-content h2 {
  margin: 0;
  font-size: 1.02rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.calculator-card-content p {
  margin: 0.35rem 0 0;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--cds-text-muted);
}

.calculators-actions {
  margin-top: var(--cds-space-xl);
  display: flex;
  justify-content: center;
}

.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.7rem 1.1rem;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--cds-primary) 45%, transparent);
  color: color-mix(in srgb, var(--cds-primary) 85%, #6b3000);
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
}

@media (min-width: 768px) {
  .calculators-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1080px) {
  .calculators-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
