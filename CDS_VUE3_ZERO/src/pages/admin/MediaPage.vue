<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Gestión de Medios</h1>
        <p>Subir y organizar imágenes en Cloudinary.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="loadingCatalog" @click="loadCatalog">
          {{ loadingCatalog ? 'Cargando...' : 'Actualizar catálogo' }}
        </button>
        <button class="btn-secondary" :disabled="importing" @click="importFromCloudinary">
          {{ importing ? `Importando... (${importProgress})` : 'Importar desde Cloudinary' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>
    <p v-if="success" class="admin-success">{{ success }}</p>

    <section class="summary-grid">
      <article class="summary-card">
        <span>Total registradas</span>
        <strong>{{ images.length }}</strong>
      </article>
      <article class="summary-card">
        <span>Instrumentos</span>
        <strong>{{ countByFolder('instrumentos') }}</strong>
      </article>
      <article class="summary-card">
        <span>Inventario</span>
        <strong>{{ countByFolder('inventario') }}</strong>
      </article>
    </section>

    <MediaUploadPanel
      v-model:destination="destination"
      :queue="queue"
      :uploading="uploading"
      :upload-progress="uploadProgress"
      :upload-validation-error="uploadValidationError"
      :format-bytes="formatBytes"
      :queue-path="queuePath"
      :status-label="statusLabel"
      @files-selected="addToQueue"
      @upload-all="uploadAll"
      @clear-queue="clearQueue"
    />

    <MediaBindingsPanel
      :bindings="bindings"
      :loading-bindings="loadingBindings"
      :show-binding-form="showBindingForm"
      :saving-binding="savingBinding"
      :is-editing-binding="isEditingBinding"
      :picker-search="pickerSearch"
      :picker-filtered="pickerFiltered"
      :binding-form="bindingForm"
      :binding-pending-delete="bindingPendingDelete"
      :deleting-binding="deletingBinding"
      :thumb="thumb"
      :short-name="shortName"
      @toggle-binding-form="toggleBindingForm"
      @update-binding-field="updateBindingField"
      @update:picker-search="pickerSearch = $event"
      @select-asset="selectBindingAsset"
      @save-binding="saveBinding"
      @edit-binding="editBinding"
      @request-delete-binding="deleteBinding"
      @cancel-delete-binding="cancelDeleteBinding"
      @confirm-delete-binding="confirmDeleteBinding"
    />

    <MediaCatalogPanel
      v-model:search="search"
      v-model:folder-filter="folderFilter"
      v-model:delete-from-cloudinary="deleteFromCloudinary"
      :images="images"
      :filtered="filtered"
      :loading-catalog="loadingCatalog"
      :flat-folder-tree="flatFolderTree"
      :asset-pending-delete="assetPendingDelete"
      :deleting-asset="deletingAsset"
      :thumb="thumb"
      :short-name="shortName"
      :format-bytes="formatBytes"
      @rename="renameAsset"
      @request-delete="requestDeleteAsset"
      @cancel-delete="cancelDeleteAsset"
      @confirm-delete="confirmDeleteAsset"
    />
  </main>
</template>

<script setup>
import MediaBindingsPanel from '@/components/admin/MediaBindingsPanel.vue'
import MediaCatalogPanel from '@/components/admin/MediaCatalogPanel.vue'
import MediaUploadPanel from '@/components/admin/MediaUploadPanel.vue'
import { useMediaAdminPage } from '@/composables/useMediaAdminPage'

const {
  images,
  loadingCatalog,
  error,
  success,
  search,
  folderFilter,
  flatFolderTree,
  importing,
  importProgress,
  destination,
  queue,
  uploading,
  uploadProgress,
  uploadValidationError,
  assetPendingDelete,
  deletingAsset,
  deleteFromCloudinary,
  bindings,
  loadingBindings,
  showBindingForm,
  savingBinding,
  pickerSearch,
  isEditingBinding,
  bindingPendingDelete,
  deletingBinding,
  bindingForm,
  filtered,
  pickerFiltered,
  countByFolder,
  loadCatalog,
  importFromCloudinary,
  addToQueue,
  uploadAll,
  clearQueue,
  renameAsset,
  requestDeleteAsset,
  cancelDeleteAsset,
  confirmDeleteAsset,
  saveBinding,
  toggleBindingForm,
  editBinding,
  updateBindingField,
  selectBindingAsset,
  deleteBinding,
  cancelDeleteBinding,
  confirmDeleteBinding,
  thumb,
  shortName,
  queuePath,
  formatBytes,
  statusLabel,
} = useMediaAdminPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped src="./mediaPageShared.css"></style>
