<template>
  <section class="inventory-alerts" data-testid="inventory-alerts">
    <div class="inventory-alerts__header">
      <div>
        <p class="eyebrow">Monitoreo</p>
        <h4>Alertas de inventario</h4>
      </div>
      <strong>{{ totalAlerts }} activas</strong>
    </div>

    <p v-if="!totalAlerts" class="inventory-alerts__empty">Sin alertas activas. El stock disponible está por sobre los mínimos.</p>

    <div v-else class="inventory-alerts__grid">
      <article
        v-for="group in visibleGroups"
        :key="group.key"
        class="inventory-alerts__group"
        :class="`inventory-alerts__group--${group.key}`"
      >
        <header>
          <strong>{{ group.title }}</strong>
          <span>{{ group.items.length }} item{{ group.items.length === 1 ? '' : 's' }}</span>
        </header>
        <ul>
          <li v-for="item in group.items.slice(0, 5)" :key="item.id">
            <span>{{ item.sku }} · {{ item.name }}</span>
            <small>{{ item.available_stock }} disp. / min {{ item.min_stock }}</small>
          </li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] }
})

function resolveLevel(item) {
  if (item?.stock_alert_level) return item.stock_alert_level

  const available = Number(item?.available_stock ?? item?.stock ?? item?.quantity ?? 0)
  const minStock = Number(item?.min_stock ?? item?.min_quantity ?? 0)
  if (minStock <= 0) return null
  if (available <= Math.max(1, Math.ceil(minStock * 0.05))) return 'critical_5'
  if (available <= Math.max(1, Math.ceil(minStock * 0.2))) return 'high_20'
  if (available <= Math.max(1, Math.ceil(minStock * 0.5))) return 'medium_50'
  if (available <= minStock) return 'low_min'
  return null
}

const groups = computed(() => {
  const seed = [
    { key: 'critical_5', title: 'Crítico 5%', items: [] },
    { key: 'high_20', title: 'Bajo 20%', items: [] },
    { key: 'medium_50', title: 'Bajo 50%', items: [] },
    { key: 'low_min', title: 'Bajo mínimo', items: [] },
  ]

  for (const item of props.items) {
    const level = resolveLevel(item)
    if (!level) continue
    const bucket = seed.find((group) => group.key === level)
    if (bucket) {
      bucket.items.push(item)
    }
  }

  return seed
})

const visibleGroups = computed(() => groups.value.filter((group) => group.items.length > 0))
const totalAlerts = computed(() => visibleGroups.value.reduce((sum, group) => sum + group.items.length, 0))
</script>
