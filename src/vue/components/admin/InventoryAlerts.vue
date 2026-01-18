<template>
  <section class="alerts">
    <h4>Alertas de Inventario</h4>
    <ul>
      <li v-for="item in lowStock" :key="item.id">
        {{ item.name }} ({{ item.quantity }} / min {{ item.min_quantity }})
      </li>
    </ul>
    <p v-if="!lowStock.length">Sin alertas.</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] }
})

const lowStock = computed(() => props.items.filter((item) => item.is_low_stock || item.quantity <= item.min_quantity))
</script>

<style scoped>
.alerts {
  border: 1px solid #fee2e2;
  border-radius: 12px;
  padding: 1rem;
  background: #fff1f2;
}
ul {
  padding-left: 1.2rem;
}
</style>
