<template>
  <article class="inventory-card">
    <div class="inventory-card__body">
      <div class="inventory-card__main">
        <img
          v-if="props.item.image_url"
          :src="props.item.image_url"
          alt=""
          class="inventory-card__image"
        />
        <div class="inventory-card__info">
          <h5 class="inventory-card__name">{{ props.item.name }}</h5>
          <span class="inventory-card__meta">{{ props.item.category || '-' }}</span>
          <span class="inventory-card__meta">
            SKU: {{ props.item.sku || props.item.sku_code || '-' }}
          </span>
        </div>
      </div>

      <div class="inventory-card__summary">
        <span class="inventory-card__stock-label">Stock</span>
        <div class="inventory-card__stock-value">
          {{ props.item.stock ?? props.item.quantity ?? props.item.cantidad ?? 0 }}
          <span v-if="props.item.stock_unit" class="inventory-card__stock-unit">
            {{ props.item.stock_unit }}
          </span>
        </div>
        <span class="inventory-card__price">${{ formatPrice(props.item.price) }}</span>
      </div>
    </div>

    <div class="inventory-card__actions">
      <button
        type="button"
        class="inventory-card__button inventory-card__button--edit"
        @click="emit('request-edit', props.item)"
      >
        Editar
      </button>
      <button
        type="button"
        class="inventory-card__button inventory-card__button--delete"
        @click="emit('request-delete', props.item)"
      >
        Eliminar
      </button>
    </div>
  </article>
</template>

<script setup>
const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['request-edit', 'request-delete'])

function formatPrice(price) {
  if (!price && price !== 0) return '-'

  try {
    return Number(price).toFixed(2)
  } catch {
    return price
  }
}
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.inventory-card {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
  width: 100%;
  max-width: none;
  padding: var(--spacer-md);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.inventory-card__body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--spacer-md);
  align-items: center;
}

.inventory-card__main {
  display: flex;
  align-items: center;
  gap: var(--spacer-md);
  min-width: 0;
}

.inventory-card__image {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  object-fit: cover;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-light);
}

.inventory-card__info {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-sm);
  min-width: 0;
}

.inventory-card__name {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--text-lg);
  font-weight: 700;
}

.inventory-card__meta {
  color: var(--color-dark);
  font-size: var(--text-sm);
  line-height: 1.4;
  opacity: 0.7;
}

.inventory-card__summary {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--spacer-sm);
  text-align: right;
  color: var(--color-dark);
}

.inventory-card__stock-label,
.inventory-card__price,
.inventory-card__stock-unit {
  font-size: var(--text-sm);
}

.inventory-card__stock-value {
  font-size: var(--text-lg);
  font-weight: 700;
}

.inventory-card__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacer-sm);
}

.inventory-card__button {
  min-height: 44px;
  padding: 0.625rem 0.875rem;
  border: 0;
  border-radius: var(--radius-sm);
  color: var(--color-white);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
}

.inventory-card__button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.inventory-card__button--edit {
  background: var(--color-primary);
}

.inventory-card__button--delete {
  background: var(--color-danger);
}

@include media-breakpoint-down(md) {
  .inventory-card__body {
    grid-template-columns: 1fr;
  }

  .inventory-card__summary,
  .inventory-card__actions {
    align-items: flex-start;
    justify-content: flex-start;
    text-align: left;
  }

  .inventory-card__actions {
    flex-wrap: wrap;
  }
}
</style>
