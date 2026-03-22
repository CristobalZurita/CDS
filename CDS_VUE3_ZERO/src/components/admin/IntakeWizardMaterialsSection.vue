<template>
  <section id="materiales" class="form-section">
    <div class="section-header">
      <h2>5. Materiales</h2>
    </div>
    <div class="materials-info">
      <p>Los materiales y componentes se registran desde la OT una vez iniciado el trabajo, con stock en tiempo real del inventario.</p>
    </div>
  </section>
</template>

<script setup>
</script>

<style scoped>
.form-section {
  background: var(--cds-white);
  border-radius: var(--cds-radius-lg);
  padding: var(--intake-section-padding, 1.5rem);
  box-shadow: var(--cds-shadow-sm);
  scroll-margin-top: var(--intake-section-scroll-margin-top, 120px);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--intake-section-header-margin-bottom, 1.5rem);
  padding-bottom: var(--intake-section-header-padding-bottom, 0.75rem);
  border-bottom: 2px solid var(--cds-light-2);
}

.section-header h2 {
  margin: 0;
  font-size: var(--cds-text-lg);
  color: var(--cds-text-normal);
}

.empty-materials {
  text-align: center;
  padding: var(--intake-empty-padding, 2rem);
  color: var(--cds-text-muted);
}

.empty-materials .hint {
  font-size: var(--cds-text-sm);
  opacity: 0.7;
}

.material-item {
  display: flex;
  gap: var(--intake-material-item-gap, 0.75rem);
  align-items: flex-end;
  padding: var(--intake-material-item-padding, 1rem);
  background: var(--cds-light-1);
  border-radius: var(--cds-radius-md);
  margin-bottom: var(--intake-material-item-gap, 0.75rem);
}

.material-fields {
  display: grid;
  grid-template-columns: 2fr 1fr 2fr;
  gap: var(--intake-material-item-gap, 0.75rem);
  flex: 1;
}

@media (max-width: 768px) {
  .material-fields {
    grid-template-columns: 1fr;
  }
}
</style>
