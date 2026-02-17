<template>
  <img
    :src="src"
    :srcset="srcset"
    :sizes="sizes"
    :alt="alt"
    :loading="loading"
    :width="width"
    :height="height"
    :class="computedClass"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // Required: Image source URL
  src: {
    type: String,
    required: true,
  },
  // Optional: Alt text for accessibility
  alt: {
    type: String,
    default: 'Image',
  },
  // Optional: srcset for responsive images
  // Example: "image-small.jpg 600w, image-med.jpg 1200w, image-large.jpg 2000w"
  srcset: {
    type: String,
    default: '',
  },
  // Optional: sizes attribute for responsive images
  // Example: "(max-width: 768px) 100vw, 50vw"
  sizes: {
    type: String,
    default: '',
  },
  // Optional: 'lazy' or 'eager'. Default is 'lazy' for performance
  loading: {
    type: String,
    default: 'lazy',
    validator: (val) => ['lazy', 'eager'].includes(val),
  },
  // Optional: Image width (helps prevent layout shift)
  width: {
    type: [Number, String],
    default: null,
  },
  // Optional: Image height (helps prevent layout shift)
  height: {
    type: [Number, String],
    default: null,
  },
  // Optional: Additional CSS classes
  class: {
    type: String,
    default: '',
  },
})

// Compute final CSS classes
const computedClass = computed(() => {
  const classes = ['optimized-image']
  if (props.class) {
    classes.push(props.class)
  }
  return classes.join(' ')
})

</script>

<style scoped lang="scss">
.optimized-image {
  /* Prevent layout shift (Cumulative Layout Shift - CLS) */
  display: block;
  max-width: 100%;
  height: auto;

  /* Optimize rendering performance */
  will-change: transform;
  backface-visibility: hidden;
  transform: translateZ(0);

  /* Smooth loading fade-in (optional, can be customized) */
  opacity: 1;
  transition: opacity 0.3s ease-in-out;
}

/* Loading state (optional) */
.optimized-image[loading='lazy'] {
  opacity: 0.95;
}

/* Loaded state (optional) */
.optimized-image[loading='eager'] {
  opacity: 1;
}
</style>
