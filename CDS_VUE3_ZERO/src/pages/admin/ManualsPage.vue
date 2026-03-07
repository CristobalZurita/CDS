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
import { useManualsPage } from '@new/composables/useManualsPage'

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

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .panel-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; justify-content: space-between; align-items: center; gap: .75rem; flex-wrap: wrap; }
.admin-header h1 { margin: 0; font-size: var(--cds-text-3xl); }
.admin-header p { margin: .3rem 0 0; color: var(--cds-text-muted); }
.header-actions { display: flex; gap: .45rem; flex-wrap: wrap; }
.btn-primary, .btn-secondary, .btn-danger { min-height: 44px; padding: .65rem .9rem; border-radius: .55rem; border: 1px solid transparent; font-size: var(--cds-text-base); }
.btn-primary { border-color: var(--cds-primary); background: var(--cds-primary); color: var(--cds-white); }
.btn-secondary { border-color: color-mix(in srgb, var(--cds-light) 65%, white); background: var(--cds-white); color: var(--cds-text-normal); }
.btn-danger { border-color: #dc2626; background: #dc2626; color: #fff; }
.admin-error { margin: 0; border: 1px solid #fecaca; background: #fef2f2; color: #991b1b; border-radius: .65rem; padding: .75rem; }
.panel-card { padding: .9rem; display: grid; gap: .7rem; }
.panel-card h2 { margin: 0; font-size: var(--cds-text-xl); }
.form-grid { display: grid; gap: .6rem; grid-template-columns: 1fr; }
.form-grid.two-cols { grid-template-columns: 1fr; }
.form-grid label { display: grid; gap: .3rem; }
.form-grid span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.form-grid input, .form-grid select, table input, table select { min-height: 44px; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); border-radius: .55rem; padding: .65rem .75rem; font-size: var(--cds-text-base); }
.form-grid .full { grid-column: 1 / -1; }
.panel-actions { display: flex; justify-content: flex-end; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: .55rem; border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); vertical-align: top; }
th { color: var(--cds-text-muted); font-size: var(--cds-text-sm); }
.row-actions { display: flex; gap: .45rem; flex-wrap: wrap; }
.empty-state { margin: 0; border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .65rem; padding: .8rem; color: var(--cds-text-muted); }
@media (min-width: 900px) {
  .form-grid.two-cols { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
