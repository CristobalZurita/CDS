<template>
  <header class="wizard-header">
    <div class="header-content">
      <div>
        <h1>Nueva Orden de Trabajo</h1>
        <p class="subtitle">Ingreso único de Cliente + Equipo + OT</p>
      </div>

      <div class="progress-section">
        <div class="progress-bar">
          <div class="progress-fill"></div>
        </div>
        <span class="progress-text">{{ progress }}% completado</span>
      </div>

      <div class="codes-display">
        <div class="code-box">
          <span class="code-label">Cliente</span>
          <span class="code-value">{{ nextClientCode || '---' }}</span>
        </div>
        <div class="code-box">
          <span class="code-label">OT</span>
          <span class="code-value">{{ nextOtCode || '---' }}</span>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  nextClientCode: {
    type: String,
    default: ''
  },
  nextOtCode: {
    type: String,
    default: ''
  },
  progress: {
    type: Number,
    default: 0
  }
})

const progressScale = computed(() => {
  const normalized = Math.min(Math.max(Number(props.progress ?? 0), 0), 100)
  return String(normalized / 100)
})
</script>

<style scoped>
.wizard-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--cds-surface-1);
  backdrop-filter: blur(8px);
  border-radius: var(--cds-radius-lg);
  padding: var(--intake-header-padding, 1.25rem);
  margin-bottom: var(--intake-header-margin-bottom, 1.5rem);
  box-shadow: var(--cds-shadow-sm);
}

.header-content {
  display: flex;
  flex-wrap: wrap;
  gap: var(--intake-header-gap, 1rem);
  align-items: center;
  justify-content: space-between;
}

.wizard-header h1 {
  margin: 0;
  font-size: var(--cds-text-xl);
}

.subtitle {
  margin: 0.25rem 0 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.progress-section {
  display: flex;
  align-items: center;
  gap: var(--intake-progress-gap, 0.75rem);
  min-width: 200px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--cds-light-3);
  border-radius: var(--cds-radius-pill);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--cds-primary);
  border-radius: var(--cds-radius-pill);
  transform: scaleX(v-bind(progressScale));
  transform-origin: left center;
  transition: transform 0.3s ease;
}

.progress-text {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  white-space: nowrap;
}

.codes-display {
  display: flex;
  gap: var(--intake-header-gap, 1rem);
}

.code-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--intake-code-box-padding-block, 0.5rem) var(--intake-code-box-padding-inline, 1rem);
  background: var(--cds-light-1);
  border-radius: var(--cds-radius-md);
  min-width: 80px;
}

.code-label {
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
  text-transform: uppercase;
}

.code-value {
  font-size: var(--cds-text-lg);
  font-weight: 700;
  color: var(--cds-primary);
  font-family: monospace;
}

@media (max-width: 768px) {
  .wizard-header {
    position: relative;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .progress-section {
    order: 3;
  }

  .codes-display {
    order: 2;
    justify-content: center;
  }
}
</style>
