<!--
  @deprecated Sin consumidores activos. No exportado en business/index.js.
  No importado en ningún archivo del proyecto. Mantener hasta decidir si se reactiva.
-->
<template>
  <article class="repair-card">
    <slot />
  </article>
</template>

<style scoped>
.repair-card {
  background: var(--cds-white);
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.75rem;
  padding: 1rem;
}
</style>
