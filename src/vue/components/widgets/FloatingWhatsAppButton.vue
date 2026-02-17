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

<style scoped lang="scss">
.floating-whatsapp-btn {
  position: fixed;
  bottom: 2rem;
  left: 2rem;
  z-index: 999;
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: #25d366;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  font-size: 2rem;
  box-shadow: 0 6px 16px rgba(37, 211, 102, 0.45);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(37, 211, 102, 0.5);
    background: #1fbe59;
  }

  &:active {
    transform: translateY(-1px);
  }
}

@media (max-width: 768px) {
  .floating-whatsapp-btn {
    bottom: 1rem;
    left: 1rem;
    width: 48px;
    height: 48px;
    font-size: 1.7rem;
  }
}
</style>
