<template>
  <button class="floating-quote-btn" @click="scrollToDiagnostic" title="Cotiza tu instrumento">
    <i class="fa-solid fa-file-circle-check"></i>
    <span class="tooltip">Cotiza aquí</span>
  </button>
</template>

<script setup>
const scrollToDiagnostic = () => {
  const element = document.getElementById('diagnostico')
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<style scoped>
.floating-quote-btn {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
  transition: all 0.3s ease;
  z-index: 1000;
}

.floating-quote-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(255, 107, 53, 0.4);
}

.floating-quote-btn:active {
  transform: scale(0.95);
}

.tooltip {
  position: absolute;
  bottom: 100%;
  right: 0;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.875rem;
  white-space: nowrap;
  margin-bottom: 0.5rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s;
}

.floating-quote-btn:hover .tooltip {
  opacity: 1;
}

@media (max-width: 768px) {
  .floating-quote-btn {
    width: 50px;
    height: 50px;
    font-size: 1.25rem;
    bottom: 1rem;
    right: 1rem;
  }
}
</style>
