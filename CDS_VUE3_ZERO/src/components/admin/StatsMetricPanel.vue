<template>
  <article class="panel-card stats-panel">
    <h2 class="stats-panel-title">{{ title }}</h2>
    <ul class="stats-panel-list">
      <li v-for="item in items" :key="item.label" class="stats-panel-row">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </li>
    </ul>
  </article>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  items: { type: Array, default: () => [] }
})
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/statsPageShared.css"></style>
