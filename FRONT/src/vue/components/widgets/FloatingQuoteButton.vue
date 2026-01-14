<template>
  <div v-if="floatingButtonVisible && !loaderActive && showScrollTop" class="floating-quote-button">
    <!-- Panel lateral que muestra toda la info sin desplazar -->
    <div class="side-panel" role="region" aria-label="Reservar cita">
      <div class="side-content">
        <div class="side-title">Agenda tu hora</div>
        <div class="side-desc">Selecciona fecha y confirma tu reserva sin desplazarte.</div>
        <button class="side-cta" @click="openAppointment" type="button">COTIZA YA</button>
      </div>
    </div>

    <!-- Botón redondeado: flecha blanca sobre fondo naranja -->
    <button @click="scrollToTop" 
            class="scroll-to-top-btn"
            aria-label="Subir al inicio"
            title="Ir arriba">
      <i class="fas fa-arrow-up"></i>
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, inject } from 'vue'
const emit = defineEmits(['open-appointment'])

const floatingButtonVisible = inject("floatingButtonVisible", ref(true))
const loaderActive = inject("loaderActive", ref(true))

const showScrollTop = ref(false)

// Calcula 1/3 de la altura total del documento
const calculateOneThirdScroll = () => {
  const docHeight = document.documentElement.scrollHeight - window.innerHeight
  return docHeight / 3
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleScroll = () => {
  const oneThirdScroll = calculateOneThirdScroll()
  showScrollTop.value = window.scrollY > oneThirdScroll
}

const openAppointment = () => {
  // Emitimos para que el componente padre abra el modal de reservas
  emit('open-appointment')
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
@import '/src/scss/_variables.scss';

.floating-quote-button {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 999;

  display: flex;
  align-items: center;
  gap: 0.75rem;

  @media (max-width: 768px) {
    bottom: 1rem;
    right: 1rem;
  }
}

.scroll-to-top-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #ff8c00; // Naranja
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(255, 140, 0, 0.4);

  i {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &:hover {
    background-color: #ff6600;
    transform: translateY(-4px);
  }

  &:active {
    transform: translateY(-2px);
  }

  @media (max-width: 768px) {
    width: 45px;
    height: 45px;
    font-size: 1.1rem;
  }
}

/* Side panel that appears to the left of the circle button */
.side-panel {
  width: 300px;
  max-width: calc(100vw - 96px);
  background: white;
  color: $dark;
  border-radius: 10px;
  padding: 12px 14px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
  transform: translateX(6px);
  opacity: 1;
  transition: transform 220ms ease, opacity 220ms ease;

  @media (max-width: 1024px) {
    width: 260px;
  }

  @media (max-width: 768px) {
    display: none;
  }
}

.side-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.side-title {
  font-weight: 800;
  font-size: 1rem;
  color: #111;
}

.side-desc {
  font-size: 0.85rem;
  color: #444;
}

.side-cta {
  margin-top: 6px;
  align-self: flex-start;
  padding: 0.5rem 0.95rem;
  background: #ff8c00;
  color: white;
  border: 0;
  border-radius: 999px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(255,140,0,0.18);
  transition: transform 120ms ease, background 120ms ease;
}

.side-cta:hover { background: #ff6600; transform: translateY(-2px) }
</style>
