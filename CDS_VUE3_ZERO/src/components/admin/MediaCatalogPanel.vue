<template>
  <section class="panel-card">
    <div class="panel-head">
      <h2>Catálogo ({{ filtered.length }})</h2>
      <div class="catalog-filters">
        <input v-model.trim="searchModel" type="search" placeholder="Buscar por nombre..." />
        <select v-model="folderFilterModel">
          <option value="">Todas las carpetas</option>
          <option value="instrumentos">Instrumentos</option>
          <option value="inventario">Inventario</option>
          <option value="general">General</option>
        </select>
      </div>
    </div>

    <p v-if="loadingCatalog" class="catalog-hint">Cargando catálogo...</p>
    <p v-else-if="!images.length" class="catalog-hint">
      No hay imágenes registradas todavía. Usá la sección "Subir imágenes" — cada imagen que subas quedará registrada aquí automáticamente.
    </p>

    <div v-else class="image-grid">
      <figure v-for="img in filtered" :key="img.public_id" class="image-tile">
        <img :src="thumb(img.secure_url)" :alt="shortName(img.public_id)" loading="lazy" />
        <figcaption>
          <span class="tile-name">{{ shortName(img.public_id) }}</span>
          <span class="tile-meta">{{ formatBytes(img.bytes) }}</span>
        </figcaption>
      </figure>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  images: {
    type: Array,
    default: () => []
  },
  filtered: {
    type: Array,
    default: () => []
  },
  loadingCatalog: {
    type: Boolean,
    default: false
  },
  search: {
    type: String,
    default: ''
  },
  folderFilter: {
    type: String,
    default: ''
  },
  thumb: {
    type: Function,
    required: true
  },
  shortName: {
    type: Function,
    required: true
  },
  formatBytes: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['update:search', 'update:folderFilter'])

const searchModel = computed({
  get: () => props.search,
  set: (value) => emit('update:search', value)
})

const folderFilterModel = computed({
  get: () => props.folderFilter,
  set: (value) => emit('update:folderFilter', value)
})
</script>

<style scoped src="@/pages/admin/commonAdminPage.css"></style>
<style scoped src="@/pages/admin/mediaPageShared.css"></style>
