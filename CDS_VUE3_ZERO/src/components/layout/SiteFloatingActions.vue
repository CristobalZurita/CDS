<template>
  <div>
    <button
      v-show="showScrollTop"
      class="scroll-top"
      :class="{ 'scroll-top--cart-open': cartOpen }"
      type="button"
      aria-label="Ir arriba"
      @click="emit('scroll-top')"
    >
      <i class="fas fa-arrow-up"></i>
    </button>
  </div>
</template>

<script setup>
defineProps({
  showScrollTop: {
    type: Boolean,
    default: false
  },
  cartOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['scroll-top'])
</script>

<style scoped>
.scroll-top {
  position: fixed;
  right: 1rem;
  bottom: 1.25rem;
  width: 46px;
  height: 46px;
  border-radius: var(--cds-radius-pill);
  border: none;
  background: var(--cds-primary);
  color: var(--cds-white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  cursor: pointer;
  z-index: 999;
  box-shadow: 0 4px 14px rgba(179, 106, 60, 0.34);
  transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1), transform 0.2s, box-shadow 0.2s;
}

.scroll-top:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 20px rgba(179, 106, 60, 0.46);
}

.scroll-top.scroll-top--cart-open {
  right: calc(var(--layout-store-drawer-width, min(420px, 100vw)) + 1rem);
}

@media (min-width: 768px) {
  .scroll-top {
    right: 1.5rem;
    bottom: 1.5rem;
    width: 50px;
    height: 50px;
  }

  .scroll-top.scroll-top--cart-open {
    right: calc(var(--layout-store-drawer-width, min(420px, 100vw)) + 1.5rem);
  }
}
</style>
