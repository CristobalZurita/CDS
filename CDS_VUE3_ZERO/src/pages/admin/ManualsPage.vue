<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Manuales</h1>
        <p>Documentos tecnicos por instrumento y fuente.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="loading" @click="loadManuals">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
        <button class="btn-primary" :disabled="loading" @click="toggleForm">
          {{ showForm ? 'Cancelar' : 'Nuevo manual' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section v-if="showForm" class="panel-card">
      <h2>Crear manual</h2>
      <div class="form-grid two-cols">
        <label>
          <span>Instrumento *</span>
          <select v-model="form.instrument_id">
            <option value="">Seleccionar</option>
            <option v-for="instrument in instruments" :key="instrument.id" :value="instrument.id">
              {{ instrument.brand ? `${instrument.brand} ` : '' }}{{ instrument.model || instrument.name || `#${instrument.id}` }}
            </option>
          </select>
        </label>
        <label>
          <span>Fuente</span>
          <select v-model="form.source">
            <option value="internal">internal</option>
            <option value="external">external</option>
          </select>
        </label>
        <label class="full"><span>Titulo *</span><input v-model.trim="form.title" type="text" /></label>
        <label class="full"><span>URL (opcional)</span><input v-model.trim="form.url" type="text" placeholder="https://..." /></label>
        <label class="full"><span>Ruta archivo (opcional)</span><input v-model.trim="form.file_path" type="text" placeholder="/uploads/manuals/..." /></label>
      </div>
      <div class="panel-actions">
        <button class="btn-primary" :disabled="loading" @click="createManual">
          {{ loading ? 'Guardando...' : 'Crear manual' }}
        </button>
      </div>
    </section>

    <section class="panel-card">
      <h2>Listado ({{ manuals.length }})</h2>
      <p v-if="manuals.length === 0" class="empty-state">Sin manuales registrados.</p>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Titulo</th>
              <th>Instrumento</th>
              <th>Fuente</th>
              <th>Link</th>
              <th>Actualizado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="manual in manuals" :key="manual.id">
              <td>#{{ manual.id }}</td>
              <td>
                <template v-if="editingId === manual.id">
                  <input v-model.trim="draft.title" type="text" />
                </template>
                <template v-else>{{ manual.title }}</template>
              </td>
              <td>{{ getInstrumentName(manual.instrument_id) }}</td>
              <td>
                <template v-if="editingId === manual.id">
                  <select v-model="draft.source">
                    <option value="internal">internal</option>
                    <option value="external">external</option>
                  </select>
                </template>
                <template v-else>{{ manual.source }}</template>
              </td>
              <td>
                <template v-if="editingId === manual.id">
                  <input v-model.trim="draft.url" type="text" placeholder="https://..." />
                </template>
                <template v-else>
                  <a v-if="getManualLink(manual)" :href="getManualLink(manual)" target="_blank" rel="noopener">Abrir</a>
                  <span v-else>—</span>
                </template>
              </td>
              <td>{{ formatDate(manual.updated_at || manual.created_at) }}</td>
              <td>
                <div class="row-actions">
                  <template v-if="editingId === manual.id">
                    <button class="btn-primary" :disabled="loading" @click="saveManual(manual)">Guardar</button>
                    <button class="btn-secondary" :disabled="loading" @click="resetDraft">Cancelar</button>
                  </template>
                  <template v-else>
                    <button class="btn-secondary" :disabled="loading" @click="startEdit(manual)">Editar</button>
                    <button class="btn-danger" :disabled="loading" @click="deleteManual(manual)">Eliminar</button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useManualsPage } from '@/composables/useManualsPage'

const {
  manuals,
  instruments,
  loading,
  error,
  showForm,
  form,
  editingId,
  draft,
  formatDate,
  getInstrumentName,
  getManualLink,
  toggleForm,
  resetDraft,
  loadManuals,
  createManual,
  startEdit,
  saveManual,
  deleteManual
} = useManualsPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped>
/* Edición inline en tabla */
table input, table select { min-height: 44px; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); border-radius: .55rem; padding: .65rem .75rem; font-size: var(--cds-text-base); }
</style>
