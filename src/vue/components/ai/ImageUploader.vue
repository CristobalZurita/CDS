<template>
  <div class="uploader">
    <input type="file" accept="image/*" @change="onSelect" />
    <img v-if="preview" :src="preview" alt="preview" />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['select'])
const preview = ref('')

const onSelect = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  preview.value = URL.createObjectURL(file)
  emit('select', file)
}
</script>

<style scoped>
.uploader {
  display: grid;
  gap: 0.75rem;
}
img {
  max-width: 100%;
  border-radius: 12px;
}
</style>
