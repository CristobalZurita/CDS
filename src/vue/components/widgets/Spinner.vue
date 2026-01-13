<template>
  <div class="spinner">
    <div class="spinner-ring"></div>
  </div>
</template>

<script setup>
</script>

<style scoped lang="scss">
.spinner {
  display: inline-block;
  position: relative;
  width: 20px;
  height: 20px;
}

.spinner-ring {
  display: inline-block;
  position: absolute;
  left: 0;
  width: 100%;
  height: 100%;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #333;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
