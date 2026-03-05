<template>
  <a
    class="floating-whatsapp-btn"
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
const whatsappUrl = 'https://wa.me/56982957538'
</script>
