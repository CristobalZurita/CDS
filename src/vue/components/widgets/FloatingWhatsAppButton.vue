<template>
  <a
    class="whatsapp-btn"
    :style="buttonStyles"
    :href="whatsappUrl"
    target="_blank"
    rel="noopener noreferrer"
    aria-label="Contactar por WhatsApp"
    title="WhatsApp"
  >
    <i class="fa-brands fa-whatsapp"></i>
  </a>
</template>

<script setup>
import { computed } from "vue"
import { useResponsive } from "@/composables/useResponsive"

const whatsappUrl = 'https://wa.me/56982957538'
const { windowWidth } = useResponsive()

const buttonStyles = computed(() => {
    const isMobile = windowWidth.value <= 768

    return {
        position: 'fixed',
        bottom: isMobile ? '1rem' : '2rem',
        left: isMobile ? '1rem' : '2rem',
        zIndex: '999',
        width: isMobile ? '48px' : '54px',
        height: isMobile ? '48px' : '54px',
        borderRadius: '50%',
        background: '#25d366',
        color: '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        textDecoration: 'none',
        fontSize: isMobile ? '1.7rem' : '2rem',
        boxShadow: '0 6px 16px rgba(37, 211, 102, 0.45)',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease'
    }
})
</script>

<style scoped>
.whatsapp-btn:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(37, 211, 102, 0.5);
    background: #1fbe59;
}

.whatsapp-btn:active {
    transform: translateY(-1px);
}
</style>
