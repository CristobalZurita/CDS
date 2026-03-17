<template>
  <section class="panel-card">
    <div class="panel-head">
      <h2>Slots del sitio ({{ bindings.length }})</h2>
      <button class="btn-secondary" @click="emit('toggle-binding-form')">
        {{ showBindingForm ? 'Cancelar' : '+ Asignar imagen a slot' }}
      </button>
    </div>

    <p class="catalog-hint">
      Un slot es un lugar fijo del sitio (ej: <code>home.hero.bg</code>). Asignás una imagen y el sitio la muestra automáticamente sin tocar código.
    </p>

    <div v-if="showBindingForm" class="binding-form">
      <div class="binding-form-fields">
        <label>
          <span>Slot (clave única)</span>
          <input
            v-model.trim="slotKeyModel"
            type="text"
            placeholder="ej: home.hero.bg"
            :readonly="isEditingBinding"
            :class="{ 'binding-slot-input--readonly': isEditingBinding }"
          />
        </label>
        <label>
          <span>Nombre legible (opcional)</span>
          <input v-model.trim="labelModel" type="text" placeholder="ej: Imagen de fondo del hero" />
        </label>
      </div>

      <div class="binding-picker">
        <span class="binding-picker-label">Elegir imagen del catálogo</span>
        <input v-model.trim="pickerSearchModel" type="search" placeholder="Buscar..." class="picker-search" />
        <div class="picker-grid">
          <figure
            v-for="img in pickerFiltered"
            :key="img.public_id"
            class="picker-tile"
            :class="{ 'picker-tile--selected': bindingForm.asset_id === img.id }"
            @click="emit('select-asset', img.id)"
          >
            <img :src="thumb(img.secure_url)" :alt="shortName(img.public_id)" loading="lazy" />
            <figcaption>{{ shortName(img.public_id) }}</figcaption>
          </figure>
        </div>
      </div>

      <div class="panel-actions">
        <button
          class="btn-primary"
          :disabled="!bindingForm.slot_key || !bindingForm.asset_id || savingBinding"
          @click="emit('save-binding')"
        >
          {{ savingBinding ? 'Guardando...' : 'Guardar slot' }}
        </button>
      </div>
    </div>

    <p v-if="loadingBindings" class="catalog-hint">Cargando slots...</p>
    <p v-else-if="!bindings.length" class="catalog-hint">No hay slots asignados todavía.</p>

    <div v-else class="bindings-list">
      <div v-for="binding in bindings" :key="binding.slot_key" class="binding-row">
        <img
          v-if="binding.asset?.secure_url"
          :src="thumb(binding.asset.secure_url)"
          :alt="binding.slot_key"
          class="binding-thumb"
        />
        <div class="binding-info">
          <span class="binding-slot">{{ binding.slot_key }}</span>
          <span v-if="binding.label" class="binding-label">{{ binding.label }}</span>
          <span class="binding-name">{{ shortName(binding.asset?.public_id) }}</span>
        </div>
        <div class="binding-actions">
          <button class="btn-icon" title="Editar" @click="emit('edit-binding', binding)">✏️</button>
          <button class="btn-icon btn-icon--danger" title="Quitar" @click="emit('request-delete-binding', binding.slot_key)">✕</button>
        </div>
      </div>
    </div>

    <BaseConfirmDialog
      :open="Boolean(bindingPendingDelete)"
      title="Quitar slot"
      :message="bindingPendingDelete ? `¿Quitar el slot ${bindingPendingDelete}?` : ''"
      confirm-label="Quitar"
      :confirm-loading="deletingBinding"
      @cancel="emit('cancel-delete-binding')"
      @confirm="emit('confirm-delete-binding')"
    />
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { BaseConfirmDialog } from '@/components/base'

const props = defineProps({
  bindings: {
    type: Array,
    default: () => []
  },
  loadingBindings: {
    type: Boolean,
    default: false
  },
  showBindingForm: {
    type: Boolean,
    default: false
  },
  savingBinding: {
    type: Boolean,
    default: false
  },
  isEditingBinding: {
    type: Boolean,
    default: false
  },
  pickerSearch: {
    type: String,
    default: ''
  },
  pickerFiltered: {
    type: Array,
    default: () => []
  },
  bindingForm: {
    type: Object,
    required: true
  },
  bindingPendingDelete: {
    type: String,
    default: ''
  },
  deletingBinding: {
    type: Boolean,
    default: false
  },
  thumb: {
    type: Function,
    required: true
  },
  shortName: {
    type: Function,
    required: true
  }
})

const emit = defineEmits([
  'toggle-binding-form',
  'update-binding-field',
  'update:pickerSearch',
  'select-asset',
  'save-binding',
  'edit-binding',
  'request-delete-binding',
  'cancel-delete-binding',
  'confirm-delete-binding'
])

function updateBindingField(field, value) {
  emit('update-binding-field', { field, value })
}

const slotKeyModel = computed({
  get: () => props.bindingForm.slot_key,
  set: (value) => updateBindingField('slot_key', value)
})

const labelModel = computed({
  get: () => props.bindingForm.label,
  set: (value) => updateBindingField('label', value)
})

const pickerSearchModel = computed({
  get: () => props.pickerSearch,
  set: (value) => emit('update:pickerSearch', value)
})
</script>

<style scoped src="@/pages/admin/commonAdminPage.css"></style>
<style scoped src="@/pages/admin/mediaPageShared.css"></style>
