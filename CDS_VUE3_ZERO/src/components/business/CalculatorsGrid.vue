<template>
  <div class="calculators-grid">
    <router-link
      v-for="item in items"
      :key="item.path"
      :to="item.path"
      class="calculator-card"
    >
      <div class="calculator-card-media" :class="{ 'calculator-card-media--icon': !item.image }">
        <img v-if="item.image" :src="item.image" :alt="item.label" loading="lazy" />
        <i v-else :class="item.icon"></i>
      </div>
      <div class="calculator-card-content">
        <h3>{{ item.label }}</h3>
        <p>{{ item.description }}</p>
      </div>
    </router-link>
  </div>
</template>

<script setup>
defineProps({
  items: { type: Array, default: () => [] }
})
</script>

<style scoped src="./calculatorsPageShared.css"></style>
