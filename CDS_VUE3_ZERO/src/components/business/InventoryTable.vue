<template>
  <div class="inventory-table-wrap">
    <table class="inventory-table">
      <slot />
    </table>
  </div>
</template>

<style scoped>
.inventory-table-wrap {
  width: 100%;
  overflow: auto;
}

.inventory-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--cds-white);
}

.inventory-table :deep(th),
.inventory-table :deep(td) {
  border: 1px solid var(--cds-border-card);
  padding: 0.65rem 0.75rem;
  font-size: var(--cds-text-base);
}
</style>
