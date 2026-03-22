<template>
  <section class="panel-card catalog-panel">
    <div class="panel-head">
      <h2>Catálogo ({{ filtered.length }})</h2>
      <input v-model.trim="searchModel" type="search" placeholder="Buscar por nombre o ruta..." class="catalog-search" />
    </div>

    <div class="catalog-layout">
      <!-- Folder tree sidebar -->
      <nav class="folder-tree">
        <button
          class="folder-node"
          :class="{ 'folder-node--active': folderFilterModel === '' }"
          @click="folderFilterModel = ''"
        >
          <i class="fa-solid fa-folder-open"></i>
          <span class="folder-node-label">Todas</span>
          <span class="folder-node-count">{{ images.length }}</span>
        </button>

        <button
          v-for="node in flatFolderTree"
          :key="node.path"
          class="folder-node"
          :class="{ 'folder-node--active': folderFilterModel === node.path }"
          :style="{ paddingLeft: `${0.75 + node.depth * 1.1}rem` }"
          @click="folderFilterModel = node.path"
        >
          <i class="fa-solid fa-folder"></i>
          <span class="folder-node-label">{{ node.label }}</span>
          <span class="folder-node-count">{{ node.count }}</span>
        </button>
      </nav>

      <!-- Image grid -->
      <div class="catalog-main">
        <p v-if="loadingCatalog" class="catalog-hint">Cargando catálogo...</p>
        <p v-else-if="!images.length" class="catalog-hint">
          Sin imágenes. Usá "Importar desde Cloudinary" o subí archivos desde el panel de subida.
        </p>
        <p v-else-if="!filtered.length" class="catalog-hint">
          Sin resultados para este filtro.
        </p>

        <div v-else class="image-grid">
          <figure v-for="img in filtered" :key="img.public_id" class="image-tile">
            <div class="tile-img-wrap">
              <img :src="thumb(img.secure_url)" :alt="shortName(img.public_id)" loading="lazy" />
            </div>
            <figcaption>
              <template v-if="renamingId === img.id">
                <input
                  v-model.trim="renameValue"
                  class="rename-input"
                  type="text"
                  @keydown.enter.prevent="commitRename(img)"
                  @keydown.escape.prevent="cancelRename"
                  @click.stop
                />
                <div class="rename-actions">
                  <button class="btn-rename-ok" title="Guardar" @click.stop="commitRename(img)">✓</button>
                  <button class="btn-rename-cancel" title="Cancelar" @click.stop="cancelRename">✕</button>
                </div>
              </template>
              <template v-else>
                <span
                  class="tile-name"
                  title="Clic para renombrar"
                  @click.stop="startRename(img)"
                >{{ shortName(img.public_id) }}</span>
                <span class="tile-folder">{{ img.folder || '/' }}</span>
                <span class="tile-meta">{{ formatBytes(img.bytes) }}</span>
              </template>
            </figcaption>
            <button
              class="tile-delete-btn"
              title="Eliminar"
              @click.stop="emit('request-delete', img)"
            >✕</button>
          </figure>
        </div>
      </div>
    </div>

    <!-- Delete confirm -->
    <div v-if="assetPendingDelete" class="delete-overlay" @click.self="emit('cancel-delete')">
      <div class="delete-dialog">
        <p class="delete-dialog-title">Eliminar imagen</p>
        <p class="delete-dialog-body">
          ¿Eliminar <strong>{{ shortName(assetPendingDelete.public_id) }}</strong> del catálogo?
        </p>
        <label class="delete-cloudinary-check">
          <input
            type="checkbox"
            :checked="deleteFromCloudinary"
            @change="emit('update:deleteFromCloudinary', $event.target.checked)"
          />
          También eliminar de Cloudinary
        </label>
        <div class="delete-dialog-actions">
          <button class="btn-secondary" :disabled="deletingAsset" @click="emit('cancel-delete')">Cancelar</button>
          <button class="btn-danger" :disabled="deletingAsset" @click="emit('confirm-delete')">
            {{ deletingAsset ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  images: { type: Array, default: () => [] },
  filtered: { type: Array, default: () => [] },
  loadingCatalog: { type: Boolean, default: false },
  search: { type: String, default: '' },
  folderFilter: { type: String, default: '' },
  flatFolderTree: { type: Array, default: () => [] },
  assetPendingDelete: { type: Object, default: null },
  deletingAsset: { type: Boolean, default: false },
  deleteFromCloudinary: { type: Boolean, default: false },
  thumb: { type: Function, required: true },
  shortName: { type: Function, required: true },
  formatBytes: { type: Function, required: true },
})

const emit = defineEmits([
  'update:search',
  'update:folderFilter',
  'update:deleteFromCloudinary',
  'rename',
  'request-delete',
  'cancel-delete',
  'confirm-delete',
])

const searchModel = computed({
  get: () => props.search,
  set: (v) => emit('update:search', v),
})

const folderFilterModel = computed({
  get: () => props.folderFilter,
  set: (v) => emit('update:folderFilter', v),
})

const renamingId = ref(null)
const renameValue = ref('')

function startRename(img) {
  renamingId.value = img.id
  renameValue.value = img.public_id
}

function cancelRename() {
  renamingId.value = null
  renameValue.value = ''
}

function commitRename(img) {
  const newId = renameValue.value.trim()
  if (newId && newId !== img.public_id) {
    emit('rename', img.id, newId)
  }
  cancelRename()
}
</script>

<style scoped src="@/pages/admin/commonAdminPage.css"></style>
<style scoped src="@/pages/admin/mediaPageShared.css"></style>
<style scoped>
.catalog-panel {
  position: relative;
}

.catalog-search {
  min-height: var(--admin-control-min-height-sm, 40px);
  border: 1px solid var(--admin-neo-line, var(--cds-border-input));
  border-radius: 1.1rem;
  padding: 0.4rem 0.75rem;
  font-size: var(--admin-text-sm, var(--cds-text-sm));
  background: rgba(255, 255, 255, 0.92);
  color: var(--admin-neo-ink, var(--cds-dark));
  width: 100%;
  max-width: 320px;
}

.catalog-layout {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 1rem;
  align-items: start;
}

@media (max-width: 700px) {
  .catalog-layout {
    grid-template-columns: 1fr;
  }
}

.folder-tree {
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid var(--admin-neo-line, var(--cds-border-card));
  border-radius: var(--admin-neo-radius-sm, var(--cds-radius-sm));
  padding: 0.4rem;
  position: sticky;
  top: 1rem;
  max-height: 70vh;
  overflow-y: auto;
}

.folder-node {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  width: 100%;
  text-align: left;
  padding: 0.38rem 0.75rem;
  border: none;
  border-radius: 0.7rem;
  background: transparent;
  cursor: pointer;
  font-size: var(--admin-text-sm, var(--cds-text-sm));
  color: var(--admin-neo-ink, var(--cds-dark));
  transition: background 0.12s;
}

.folder-node:hover {
  background: rgba(236, 107, 0, 0.08);
}

.folder-node--active {
  background: rgba(236, 107, 0, 0.14);
  color: var(--cds-primary);
  font-weight: var(--cds-font-semibold);
}

.folder-node i {
  font-size: 0.8em;
  color: var(--cds-primary);
  flex-shrink: 0;
}

.folder-node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.folder-node-count {
  font-size: var(--admin-text-xs, var(--cds-text-xs));
  color: var(--admin-neo-muted, var(--cds-text-muted));
  flex-shrink: 0;
}

.catalog-main {
  min-width: 0;
}

.image-tile {
  position: relative;
}

.tile-img-wrap {
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: var(--cds-surface-2);
}

.tile-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.tile-folder {
  font-size: var(--admin-text-xs, var(--cds-text-xs));
  color: var(--admin-neo-muted, var(--cds-text-muted));
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--cds-font-family-mono, monospace);
}

.tile-name {
  cursor: pointer;
  border-bottom: 1px dashed transparent;
  transition: border-color 0.12s, color 0.12s;
}

.tile-name:hover {
  color: var(--cds-primary);
  border-bottom-color: var(--cds-primary);
}

.tile-delete-btn {
  position: absolute;
  top: 0.3rem;
  right: 0.3rem;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: none;
  background: rgba(180, 30, 30, 0.82);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.image-tile:hover .tile-delete-btn {
  display: flex;
}

.rename-input {
  width: 100%;
  font-size: var(--admin-text-xs, var(--cds-text-xs));
  border: 1px solid var(--cds-primary);
  border-radius: 0.4rem;
  padding: 0.15rem 0.3rem;
  background: #fff;
  color: var(--cds-dark);
  box-sizing: border-box;
}

.rename-actions {
  display: flex;
  gap: 3px;
  margin-top: 2px;
}

.btn-rename-ok,
.btn-rename-cancel {
  flex: 1;
  border: none;
  border-radius: 0.4rem;
  font-size: 0.7rem;
  font-weight: 700;
  cursor: pointer;
  padding: 0.1rem 0;
}

.btn-rename-ok {
  background: var(--cds-primary);
  color: #fff;
}

.btn-rename-cancel {
  background: var(--cds-surface-2);
  color: var(--cds-dark);
}

/* Delete confirm overlay */
.delete-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-dialog {
  background: var(--cds-surface-1);
  border-radius: var(--cds-radius-lg);
  padding: 1.5rem;
  max-width: 380px;
  width: 90%;
  display: grid;
  gap: 0.75rem;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
}

.delete-dialog-title {
  margin: 0;
  font-size: var(--cds-text-lg);
  font-weight: var(--cds-font-bold);
  color: var(--cds-dark);
}

.delete-dialog-body {
  margin: 0;
  font-size: var(--cds-text-base);
  color: var(--cds-text-muted);
}

.delete-cloudinary-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--cds-text-sm);
  color: var(--cds-dark);
  cursor: pointer;
}

.delete-dialog-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn-danger {
  min-height: 38px;
  padding: 0.4rem 1rem;
  border: none;
  border-radius: var(--cds-radius-sm);
  background: var(--cds-invalid-text, #c0392b);
  color: #fff;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-danger:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>
