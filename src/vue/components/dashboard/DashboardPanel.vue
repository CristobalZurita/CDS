<template>
  <div>
    <h2>Panel</h2>
    <div class="grid">
      <div class="card">Quick stats</div>
      <div class="card">Reparaciones recientes</div>
      <div class="card">Alertas de inventario</div>
    </div>
  </div>
</template>
<script setup>
// Component placeholder - integrar datos reales desde stores
</script>
<style scoped>
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.card { padding: 12px; border-radius: 6px; }
.card:first-child { background: $brand-primary; color: white; }
.card:nth-child(2) { background: $brand-accent; color: white; }
.card:nth-child(3) { background: $brand-paper; color: $brand-text; }
</style>
