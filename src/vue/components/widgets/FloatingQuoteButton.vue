<template>
  <button
    v-if="showScrollTop"
    class="scroll-to-top-btn"
    type="button"
    aria-label="Subir al inicio"
    title="Ir arriba"
    @click="scrollToTop"
  >
    <i class="fas fa-arrow-up"></i>
  </button>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const showScrollTop = ref(false)

const handleScroll = () => {
  const threshold = (document.documentElement.scrollHeight - window.innerHeight) / 3
  showScrollTop.value = window.scrollY > threshold
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  handleScroll()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped lang="scss">
@use '@/scss/core' as *;

.scroll-to-top-btn {
  position: fixed;
  bottom: 2rem;
  right: 2rem !important;
  left: auto !important;
  z-index: 999;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: $color-primary;
  color: $color-white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $text-xl;
  transition: $transition-base;
  box-shadow: 0 4px 12px rgba($color-primary, 0.4);

  &:hover {
    background-color: $color-primary-dark;
    transform: translateY(-4px);
  }

  &:active {
    transform: translateY(-2px);
  }

  @media (max-width: 768px) {
    bottom: 1rem;
    right: 1rem !important;
    left: auto !important;
    width: 45px;
    height: 45px;
    font-size: $text-lg;
  }
}
</style>
