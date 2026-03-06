<template>
  <button
    v-if="showScrollTop"
    class="scroll-btn"
    :style="buttonStyles"
    type="button"
    aria-label="Subir al inicio"
    title="Ir arriba"
    @click="scrollToTop"
  >
    <i class="fas fa-arrow-up"></i>
  </button>
</template>

<script setup>
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { useResponsive, COLORS } from "@/composables/useResponsive"

const showScrollTop = ref(false)
const { windowWidth } = useResponsive()

const buttonStyles = computed(() => {
  const isMobile = windowWidth.value <= 768

  return {
    position: 'fixed',
    bottom: isMobile ? '1rem' : '2rem',
    right: isMobile ? '1rem' : '2rem',
    left: 'auto',
    zIndex: '999',
    width: isMobile ? '45px' : '50px',
    height: isMobile ? '45px' : '50px',
    borderRadius: '50%',
    backgroundColor: COLORS.primary,
    color: COLORS.white,
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: isMobile ? '1.25rem' : '1.5rem', // $text-lg / $text-xl
    transition: 'all 0.3s ease',
    boxShadow: `0 4px 12px rgba(236, 107, 0, 0.4)` // rgba($primary, 0.4)
  }
})

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

<style scoped>
.scroll-btn:hover {
  background-color: #cc5500 !important; /* $color-primary-dark */
  transform: translateY(-4px);
}

.scroll-btn:active {
  transform: translateY(-2px);
}
</style>
