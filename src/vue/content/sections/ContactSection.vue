<template>
  <div class="stub-component">
    <slot></slot>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { default: null }
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.stub-component {
  min-height: 0;
}
</style>
