<template>
  <section id="materiales" class="form-section">
    <div class="section-header">
      <h2>5. Materiales a Utilizar</h2>
      <BaseButton
        type="button"
        variant="ghost"
        size="sm"
        @click="$emit('add-material')"
      >
        + Agregar material
      </BaseButton>
    </div>

    <div v-if="materials.length === 0" class="empty-materials">
      <p>No se han agregado materiales aún.</p>
      <p class="hint">Puedes agregarlos ahora o más tarde desde la OT.</p>
    </div>

    <div v-for="(material, index) in materials" :key="material.id" class="material-item">
      <div class="material-fields">
        <FormField
          v-model="material.sku"
          label="SKU"
          placeholder="Buscar por SKU..."
          size="sm"
        />

        <FormField
          v-model="material.quantity"
          type="number"
          label="Cantidad"
          :min="1"
          size="sm"
        />

        <FormField
          v-model="material.notes"
          label="Notas"
          placeholder="Descripción..."
          size="sm"
        />
      </div>

      <BaseButton
        type="button"
        variant="ghost"
        size="sm"
        @click="$emit('remove-material', index)"
      >
        🗑️
      </BaseButton>
    </div>
  </section>
</template>

<script setup>
import { BaseButton } from '@/components/base'
import { FormField } from '@/components/composite'

defineProps({
  materials: {
    type: Array,
    default: () => []
  }
})

defineEmits(['add-material', 'remove-material'])
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
