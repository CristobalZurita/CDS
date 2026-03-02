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
