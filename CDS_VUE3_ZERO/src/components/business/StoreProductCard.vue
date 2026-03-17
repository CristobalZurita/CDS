<template>
  <article class="product-card" data-testid="store-product-card">
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
          @click="$emit('add', product)"
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
})

defineEmits(['add'])

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
  background: rgba(255, 255, 255, 0.98);
  box-shadow: var(--cds-shadow-sm);
}

.product-visual {
  position: relative;
  min-height: 180px;
  display: grid;
  place-items: center;
  border-bottom: 1px solid var(--cds-border-card);
  background: linear-gradient(135deg, rgba(236, 107, 0, 0.10), #edf0e8);
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
  background: rgba(236, 107, 0, 0.12);
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
  min-height: 26px;
  padding: 0.15rem 0.6rem;
  border-radius: var(--cds-radius-pill);
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: 0.78rem;
  font-weight: 700;
}

.stock-badge--warning {
  background: var(--cds-warning);
  color: var(--cds-dark);
}

.stock-badge--info {
  background: var(--cds-info);
  color: var(--cds-white);
}

.product-body {
  padding: var(--cds-space-md);
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-xs);
  flex: 1;
}

.product-family {
  margin: 0;
  color: var(--cds-primary);
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.product-body h2 {
  margin: 0;
  font-size: 1rem;
  line-height: 1.3;
  color: var(--cds-dark);
}

.product-sku {
  margin: 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.product-description {
  margin: 0;
  font-size: 0.9rem;
  color: var(--cds-text-muted);
  line-height: 1.5;
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
  gap: 0.15rem;
}

.price-block strong {
  font-size: var(--cds-text-lg);
  font-weight: 700;
  color: var(--cds-dark);
}

.price-block small {
  font-size: 0.8rem;
  color: var(--cds-text-muted);
}

.btn-add {
  min-height: 38px;
  padding: 0.45rem 0.85rem;
  border-radius: var(--cds-radius-sm);
  border: none;
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s, transform 0.15s;
}

.btn-add:hover:not(:disabled) {
  background: color-mix(in srgb, var(--cds-primary) 85%, black);
  transform: translateY(-1px);
}

.btn-add:disabled {
  opacity: 0.55;
  cursor: default;
}
</style>
