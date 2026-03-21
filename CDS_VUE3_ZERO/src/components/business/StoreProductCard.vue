<template>
  <article
    class="product-card"
    tabindex="0"
    data-testid="store-product-card"
    @click="$emit('view', product)"
    @keydown.enter.prevent.self="$emit('view', product)"
    @keydown.space.prevent.self="$emit('view', product)"
  >
    <div class="product-visual">
      <img
        v-if="imageSrc"
        :src="imageSrc"
        :alt="product.name"
        class="product-image"
        loading="lazy"
      />
      <div v-else class="product-placeholder">
        {{ placeholderText }}
      </div>

      <span
        v-if="stockBadge"
        :class="['stock-badge', stockBadge.variant && `stock-badge--${stockBadge.variant}`]"
      >
        {{ stockBadge.text }}
      </span>

      <span v-if="qtyInCart > 0" class="cart-badge">
        {{ qtyInCart }} en carrito
      </span>
    </div>

    <div class="product-body">
      <p class="product-family">{{ product.family || product.category || 'Repuesto' }}</p>
      <h2>{{ product.name }}</h2>
      <p class="product-sku">{{ product.sku }}</p>
      <p class="product-description">{{ description }}</p>

      <div class="product-footer">
        <div class="price-block">
          <strong>{{ priceLabel }}</strong>
          <small>{{ product.category || 'Sin categoría' }}</small>
        </div>

        <button
          class="btn-add"
          data-testid="store-add-to-cart"
          :disabled="!canAdd"
          @click.stop="$emit('add', product)"
        >
          {{ buttonLabel }}
        </button>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
  imageSrc: {
    type: String,
    default: '',
  },
  description: {
    type: String,
    default: '',
  },
  priceLabel: {
    type: String,
    default: '',
  },
  canAdd: {
    type: Boolean,
    default: false,
  },
  buttonLabel: {
    type: String,
    default: 'Agregar',
  },
  qtyInCart: {
    type: Number,
    default: 0,
  },
})

defineEmits(['add', 'view'])

const placeholderText = computed(() => String(props.product?.sku || 'RP').slice(0, 3).toUpperCase())

const stockBadge = computed(() => {
  const available = Number(props.product?.available_stock || 0)
  const sellable = Number(props.product?.sellable_stock || 0)
  const unit = props.product?.stock_unit || 'u'

  if (available <= 0) {
    return { text: 'Sin stock', variant: 'warning' }
  }
  if (sellable <= 0) {
    return { text: 'Reservado taller', variant: 'warning' }
  }
  if (props.product?.is_low_stock) {
    return { text: `Últimas ${sellable} ${unit}`, variant: 'info' }
  }
  return { text: `${sellable} ${unit}`, variant: '' }
})
</script>

<style scoped>
.product-card {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-lg);
  overflow: hidden;
  background: var(--cds-surface-1);
  box-shadow: var(--cds-shadow-sm);
  font-family: var(--layout-public-font-family-base, var(--cds-font-family-base), sans-serif);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.product-card:hover,
.product-card:focus-visible {
  transform: translateY(-2px);
  box-shadow: 0 18px 36px rgba(36, 21, 14, 0.2);
  border-color: var(--cds-primary);
  outline: none;
}

.product-visual {
  position: relative;
  min-height: 180px;
  display: grid;
  place-items: center;
  border-bottom: 1px solid var(--cds-border-card);
  background: var(--cds-surface-2);
}

.product-image {
  max-width: 100%;
  max-height: 180px;
  object-fit: contain;
}

.product-placeholder {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--cds-surface-1);
  color: var(--cds-primary);
  font-weight: 800;
  letter-spacing: 0.08em;
  font-size: 1rem;
}

.stock-badge {
  position: absolute;
  top: 0.6rem;
  left: 0.6rem;
  display: inline-flex;
  align-items: center;
  min-height: calc(26px * var(--cds-type-scale, 1));
  padding: calc(0.15rem * var(--cds-type-scale, 1)) calc(0.6rem * var(--cds-type-scale, 1));
  border-radius: var(--cds-radius-pill);
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: var(--layout-public-text-label, 0.78rem);
  font-weight: 700;
}

.cart-badge {
  position: absolute;
  right: 0.6rem;
  bottom: 0.6rem;
  display: inline-flex;
  align-items: center;
  min-height: calc(26px * var(--cds-type-scale, 1));
  padding: calc(0.15rem * var(--cds-type-scale, 1)) calc(0.65rem * var(--cds-type-scale, 1));
  border-radius: var(--cds-radius-pill);
  background: #181b1f;
  color: var(--cds-white);
  font-size: var(--layout-public-text-label, 0.76rem);
  font-weight: 700;
}

.stock-badge--warning {
  background: var(--cds-warning);
  color: #fff7eb;
}

.stock-badge--info {
  background: var(--cds-info);
  color: var(--cds-white);
}

.product-body {
  padding: calc(var(--cds-space-md) * var(--cds-type-scale, 1));
  display: flex;
  flex-direction: column;
  gap: calc(var(--cds-space-xs) * var(--cds-type-scale, 1));
  flex: 1;
}

.product-family {
  margin: 0;
  color: var(--cds-primary);
  font-size: var(--layout-public-text-label, 0.8rem);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.product-body h2 {
  margin: 0;
  font-family: var(--layout-public-font-family-heading, var(--layout-public-font-family-base, var(--cds-font-family-base)));
  font-size: var(--layout-public-text-brand, 1rem);
  line-height: 1.12;
  letter-spacing: -0.01em;
  color: var(--cds-dark);
}

.product-sku {
  margin: 0;
  color: var(--cds-text-muted);
  font-size: var(--layout-public-text-meta, var(--cds-text-sm));
}

.product-description {
  margin: 0;
  font-size: var(--layout-public-text-body, 0.9rem);
  color: var(--cds-text-muted);
  line-height: 1.64;
}

.product-footer {
  margin-top: auto;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--cds-space-sm);
  flex-wrap: wrap;
}

.price-block {
  display: flex;
  flex-direction: column;
  gap: calc(0.15rem * var(--cds-type-scale, 1));
}

.price-block strong {
  font-size: var(--layout-public-text-brand, var(--cds-text-lg));
  font-weight: 700;
  color: var(--cds-dark);
}

.price-block small {
  font-size: var(--layout-public-text-label, 0.8rem);
  color: var(--cds-text-muted);
}

.btn-add {
  min-height: calc(38px * var(--cds-type-scale, 1));
  padding: calc(0.45rem * var(--cds-type-scale, 1)) calc(0.85rem * var(--cds-type-scale, 1));
  border-radius: var(--cds-radius-sm);
  border: none;
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: var(--layout-public-text-meta, 0.9rem);
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s, transform 0.15s;
}

.btn-add:hover:not(:disabled) {
  background: var(--cds-dark);
  transform: translateY(-1px);
}

.btn-add:disabled {
  opacity: 0.55;
  cursor: default;
}
</style>
