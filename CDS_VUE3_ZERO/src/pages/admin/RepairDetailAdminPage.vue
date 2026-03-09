<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Detalle de reparacion</h1>
        <p v-if="repair">{{ repair.repair_code || repair.repair_number }} · {{ repair.client?.name || 'Sin cliente' }}</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="goBack">Volver</button>
        <button class="btn-secondary" :disabled="!repair" @click="goToPurchaseRequests">Compras OT</button>
      </div>
    </header>

    <section v-if="loading" class="panel-card"><p class="empty-state">Cargando reparacion...</p></section>
    <section v-else-if="!repair" class="panel-card"><p class="empty-state">No se encontro la reparacion solicitada.</p></section>

    <template v-else>
      <p v-if="error" class="admin-error">{{ error }}</p>

      <section class="summary-grid">
        <article class="summary-card">
          <span>Estado</span>
          <strong :class="statusClass">{{ statusLabel }}</strong>
        </article>
        <article class="summary-card">
          <span>Prioridad</span>
          <strong :class="priorityClass">{{ priorityLabel }}</strong>
        </article>
        <article class="summary-card">
          <span>Total OT</span>
          <strong>{{ formatCurrency(repair.total_cost) }}</strong>
        </article>
        <article class="summary-card">
          <span>Abonado</span>
          <strong>{{ formatCurrency(repair.paid_amount) }}</strong>
        </article>
      </section>

      <section class="panel-card">
        <h2>Informacion general</h2>
        <div class="detail-grid">
          <article>
            <p><strong>Cliente:</strong> {{ repair.client?.name || '—' }}</p>
            <p><strong>Codigo cliente:</strong> {{ repair.client?.client_code || '—' }}</p>
            <p><strong>Instrumento:</strong> {{ repair.device?.model || '—' }}</p>
            <p><strong>Serial:</strong> {{ repair.device?.serial_number || '—' }}</p>
          </article>
          <article>
            <p><strong>Problema:</strong> {{ repair.problem_reported || '—' }}</p>
            <p><strong>Diagnostico:</strong> {{ repair.diagnosis || '—' }}</p>
            <p><strong>Trabajo:</strong> {{ repair.work_performed || '—' }}</p>
            <p><strong>Archivada:</strong> {{ isArchived ? 'Si' : 'No' }}</p>
          </article>
        </div>
      </section>

      <section class="panel-card">
        <h2>Estado y costos</h2>
        <div class="form-grid two-cols">
          <label>
            <span>Estado OT</span>
            <select v-model.number="statusDraft">
              <option v-for="status in statusOptions" :key="status.id" :value="status.id">{{ status.id }} - {{ status.label }}</option>
            </select>
          </label>
          <div class="field-actions">
            <button class="btn-primary" :disabled="updatingStatus" @click="updateStatus">
              {{ updatingStatus ? 'Guardando...' : 'Actualizar estado' }}
            </button>
          </div>

          <label class="full"><span>Diagnostico</span><textarea v-model.trim="editForm.diagnosis" rows="3"></textarea></label>
          <label class="full"><span>Trabajo realizado</span><textarea v-model.trim="editForm.work_performed" rows="3"></textarea></label>

          <label><span>Costo partes</span><input v-model.number="editForm.parts_cost" type="number" min="0" /></label>
          <label><span>Costo mano de obra</span><input v-model.number="editForm.labor_cost" type="number" min="0" /></label>
          <label><span>Costo adicional</span><input v-model.number="editForm.additional_cost" type="number" min="0" /></label>
          <label><span>Descuento</span><input v-model.number="editForm.discount" type="number" min="0" /></label>
          <label><span>Total</span><input v-model.number="editForm.total_cost" type="number" min="0" /></label>
          <label><span>Abonado</span><input v-model.number="editForm.paid_amount" type="number" min="0" /></label>
          <label>
            <span>Medio de pago</span>
            <select v-model="editForm.payment_method">
              <option value="">Sin definir</option>
              <option value="cash">Efectivo</option>
              <option value="web">Web</option>
              <option value="transfer">Transferencia</option>
            </select>
          </label>
        </div>
        <div class="panel-actions">
          <button class="btn-primary" :disabled="savingRepair" @click="saveRepairFields">
            {{ savingRepair ? 'Guardando...' : 'Guardar cambios tecnicos' }}
          </button>
        </div>
      </section>

      <section class="panel-card">
        <h2>Firma y foto de cliente</h2>
        <div class="action-grid">
          <button class="btn-secondary" :disabled="performingAction" @click="requestSignature('ingreso')">Solicitar firma ingreso</button>
          <button class="btn-secondary" :disabled="performingAction" @click="requestSignature('retiro')">Solicitar firma retiro</button>
          <button class="btn-secondary" :disabled="performingAction" @click="requestPhotoUpload">Solicitar foto cliente</button>
        </div>
        <p><strong>Firma ingreso:</strong> {{ repair.signature_ingreso_path ? 'OK' : 'Pendiente' }}</p>
        <p><strong>Firma retiro:</strong> {{ repair.signature_retiro_path ? 'OK' : 'Pendiente' }}</p>
        <p v-if="signatureLink" class="link-line"><strong>Link firma:</strong> <a :href="signatureLink" target="_blank" rel="noopener">{{ signatureLink }}</a></p>
        <p v-if="photoUploadLink" class="link-line"><strong>Link foto:</strong> <a :href="photoUploadLink" target="_blank" rel="noopener">{{ photoUploadLink }}</a></p>
      </section>

      <section class="panel-card">
        <div class="panel-head">
          <h2>Fotos ({{ photos.length }})</h2>
          <button class="btn-secondary" @click="showPhotoUpload = !showPhotoUpload">
            {{ showPhotoUpload ? 'Cerrar carga' : 'Agregar foto' }}
          </button>
        </div>

        <div v-if="showPhotoUpload" class="form-grid two-cols panel-nested">
          <label class="full"><span>Archivo</span><input type="file" accept="image/*" @change="onFileSelected" /></label>
          <label><span>Tipo</span><select v-model="newPhotoType"><option value="general">general</option><option value="before">before</option><option value="after">after</option><option value="damage">damage</option><option value="component">component</option><option value="client">client</option></select></label>
          <label><span>Descripcion</span><input v-model.trim="newPhotoCaption" type="text" placeholder="Descripcion opcional" /></label>
          <div class="field-actions full">
            <button class="btn-primary" :disabled="uploadingPhoto || !selectedFile" @click="uploadPhoto">
              {{ uploadingPhoto ? 'Subiendo...' : 'Subir foto' }}
            </button>
          </div>
        </div>

        <p v-if="photos.length === 0" class="empty-state">Sin fotos registradas.</p>
        <div v-else class="photos-grid">
          <article v-for="photo in photos" :key="photo.id" class="photo-card">
            <img :src="photo.resolved_photo_url" :alt="photo.caption || 'Foto OT'" />
            <div class="photo-meta">
              <span>{{ photo.photo_type }}</span>
              <small>{{ photo.caption || 'Sin descripcion' }}</small>
              <small>{{ formatDate(photo.created_at) }}</small>
            </div>
          </article>
        </div>
      </section>

      <section class="panel-card">
        <div class="panel-head">
          <h2>Notas ({{ notes.length }})</h2>
          <button class="btn-secondary" @click="showNoteForm = !showNoteForm">
            {{ showNoteForm ? 'Cerrar nota' : 'Agregar nota' }}
          </button>
        </div>

        <div v-if="showNoteForm" class="form-grid panel-nested">
          <label><span>Tipo</span><select v-model="newNoteType"><option value="internal">internal</option><option value="public">public</option><option value="technical">technical</option></select></label>
          <label><span>Nota</span><textarea v-model.trim="newNote" rows="3"></textarea></label>
          <div class="field-actions">
            <button class="btn-primary" :disabled="savingNote" @click="addNote">
              {{ savingNote ? 'Guardando...' : 'Guardar nota' }}
            </button>
          </div>
        </div>

        <p v-if="notes.length === 0" class="empty-state">Sin notas registradas.</p>
        <div v-else class="notes-list">
          <article v-for="note in notes" :key="note.id" class="note-card" :class="noteTypeClass(note.note_type)">
            <header>
              <strong>{{ note.note_type }}</strong>
              <small>{{ formatDate(note.created_at) }}</small>
            </header>
            <p>{{ note.note }}</p>
          </article>
        </div>
      </section>

      <section class="panel-card">
        <h2>Acciones</h2>
        <div class="action-grid">
          <button class="btn-secondary" :disabled="performingAction" @click="notifyClient">Enviar resumen al cliente</button>
          <button class="btn-secondary" :disabled="downloadingClosurePdf" @click="downloadClosurePdf">
            {{ downloadingClosurePdf ? 'Generando PDF...' : 'Descargar cierre OT' }}
          </button>
          <button v-if="!isArchived" class="btn-danger" :disabled="performingAction" @click="archiveRepair">Archivar OT</button>
          <button v-else class="btn-primary" :disabled="performingAction" @click="reactivateRepair">Reactivar OT</button>
        </div>
      </section>
    </template>
  </main>
</template>

<script setup>
import { useRepairDetailAdminPage } from '@/composables/useRepairDetailAdminPage'

const {
  repair,
  photos,
  notes,
  loading,
  error,
  statusOptions,
  statusDraft,
  editForm,
  updatingStatus,
  savingRepair,
  performingAction,
  uploadingPhoto,
  savingNote,
  downloadingClosurePdf,
  showPhotoUpload,
  selectedFile,
  newPhotoCaption,
  newPhotoType,
  showNoteForm,
  newNote,
  newNoteType,
  signatureLink,
  photoUploadLink,
  isArchived,
  statusLabel,
  statusClass,
  priorityLabel,
  priorityClass,
  formatDate,
  formatCurrency,
  noteTypeClass,
  updateStatus,
  saveRepairFields,
  archiveRepair,
  reactivateRepair,
  notifyClient,
  requestSignature,
  requestPhotoUpload,
  onFileSelected,
  uploadPhoto,
  addNote,
  downloadClosurePdf,
  goToPurchaseRequests,
  goBack
} = useRepairDetailAdminPage()
</script>

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .panel-card, .summary-card, .panel-nested, .photo-card, .note-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; justify-content: space-between; align-items: center; gap: .75rem; flex-wrap: wrap; }
.admin-header h1 { margin: 0; font-size: var(--cds-text-3xl); }
.admin-header p { margin: .3rem 0 0; color: var(--cds-text-muted); }
.header-actions { display: flex; gap: .45rem; flex-wrap: wrap; }
.btn-primary, .btn-secondary, .btn-danger { min-height: 44px; padding: .65rem .9rem; border-radius: .55rem; border: 1px solid transparent; font-size: var(--cds-text-base); }
.btn-primary { border-color: var(--cds-primary); background: var(--cds-primary); color: var(--cds-white); }
.btn-secondary { border-color: color-mix(in srgb, var(--cds-light) 65%, white); background: var(--cds-white); color: var(--cds-text-normal); }
.btn-danger { border-color: #dc2626; background: #dc2626; color: #fff; }
.admin-error { margin: 0; border: 1px solid #fecaca; background: #fef2f2; color: #991b1b; border-radius: .65rem; padding: .75rem; }
.summary-grid { display: grid; gap: .65rem; grid-template-columns: repeat(1, minmax(0, 1fr)); }
.summary-card { padding: .7rem; display: grid; gap: .2rem; }
.summary-card span { color: var(--cds-text-muted); font-size: var(--cds-text-sm); }
.summary-card strong { font-size: var(--cds-text-xl); }
.status-pending { color: #b45309; }
.status-progress { color: #0369a1; }
.status-success { color: #15803d; }
.status-archived { color: #334155; }
.status-neutral { color: var(--cds-text-normal); }
.priority-high { color: #dc2626; }
.priority-normal { color: #0369a1; }
.priority-low { color: #15803d; }
.panel-card { padding: .9rem; display: grid; gap: .7rem; }
.panel-card h2 { margin: 0; font-size: var(--cds-text-xl); }
.panel-head { display: flex; justify-content: space-between; align-items: center; gap: .65rem; flex-wrap: wrap; }
.detail-grid { display: grid; gap: .8rem; grid-template-columns: repeat(1, minmax(0, 1fr)); }
.detail-grid p { margin: .25rem 0; }
.form-grid { display: grid; gap: .6rem; grid-template-columns: 1fr; }
.form-grid.two-cols { grid-template-columns: 1fr; }
.form-grid label { display: grid; gap: .3rem; }
.form-grid span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.form-grid input, .form-grid textarea, .form-grid select { min-height: 44px; border-radius: .55rem; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); padding: .65rem .75rem; font-size: var(--cds-text-base); }
.form-grid textarea { min-height: 92px; resize: vertical; }
.form-grid .full { grid-column: 1 / -1; }
.panel-actions { display: flex; justify-content: flex-end; }
.field-actions { display: flex; align-items: end; }
.action-grid { display: flex; gap: .45rem; flex-wrap: wrap; }
.link-line { margin: 0; word-break: break-all; }
.panel-nested { padding: .75rem; display: grid; gap: .6rem; }
.photos-grid { display: grid; gap: .65rem; grid-template-columns: repeat(1, minmax(0, 1fr)); }
.photo-card { overflow: hidden; }
.photo-card img { width: 100%; height: 180px; object-fit: cover; display: block; }
.photo-meta { padding: .6rem; display: grid; gap: .2rem; font-size: var(--cds-text-sm); }
.notes-list { display: grid; gap: .5rem; }
.note-card { padding: .65rem; display: grid; gap: .35rem; }
.note-card header { display: flex; justify-content: space-between; gap: .45rem; }
.note-card p { margin: 0; white-space: pre-wrap; }
.note-internal { border-left: 4px solid #64748b; }
.note-public { border-left: 4px solid #0284c7; }
.note-technical { border-left: 4px solid #a16207; }
.empty-state { margin: 0; border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .65rem; padding: .8rem; color: var(--cds-text-muted); }
@media (min-width: 900px) {
  .summary-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .detail-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .form-grid.two-cols { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .photos-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
</style>
