<template>
  <div class="inventory-card p-3 border rounded bg-white shadow-sm">
    <div class="d-flex align-items-center">
      <div class="flex-grow-1 d-flex align-items-center">
        <img
          v-if="item.image_url"
          :src="item.image_url"
          alt=""
          class="img-thumbnail me-3"
          style="width:64px;height:64px;object-fit:cover;"
        />
        <div>
          <h5 class="mb-0">{{ item.name }}</h5>
          <small class="text-muted">{{ item.category || '-' }}</small>
          <div><small class="text-muted">SKU: {{ item.sku || item.sku_code || '-' }}</small></div>
        </div>
      </div>
      <div class="text-end ms-3">
        <div class="small text-muted">Stock</div>
        <div class="fs-5 fw-bold">{{ item.stock ?? item.quantity ?? item.cantidad ?? 0 }} <small class="fw-normal">{{ item.stock_unit || '' }}</small></div>
        <div class="small text-muted">${{ formatPrice(item.price) }}</div>
        <div class="mt-2 d-flex gap-2 justify-content-end">
          <button @click="$emit('request-edit', item)" class="btn btn-sm btn-primary">Editar</button>
          <button @click="$emit('request-delete', item)" class="btn btn-sm btn-danger">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InventoryCard',
  props: {
    item: {
      type: Object,
      required: true
    }
  },
  methods: {
    formatPrice(p) {
      if (!p && p !== 0) return '-'
      try {
        return Number(p).toFixed(2)
      } catch (e) {
        return p
      }
    }
  }
}
</script>

<style scoped>
.inventory-card { max-width: 420px }
</style>
