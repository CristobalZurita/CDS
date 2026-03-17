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

<style scoped src="./commonAdminPage.css"></style>
<style scoped>
/* Status / priority color utilities */
.status-pending { color: var(--cds-warning-text); }
.status-progress { color: var(--cds-info); }
.status-success { color: var(--cds-success); }
.status-archived { color: var(--cds-light-7); }
.status-neutral { color: var(--cds-text-normal); }
.priority-high { color: var(--cds-danger); }
.priority-normal { color: var(--cds-info); }
.priority-low { color: var(--cds-success); }
/* Layout helpers */
.panel-head { display: flex; justify-content: space-between; align-items: center; gap: .65rem; flex-wrap: wrap; }
.detail-grid { display: grid; gap: .8rem; grid-template-columns: repeat(1, minmax(0, 1fr)); }
.detail-grid p { margin: .25rem 0; }
.field-actions { display: flex; align-items: end; }
.action-grid { display: flex; gap: .45rem; flex-wrap: wrap; }
.link-line { margin: 0; word-break: break-all; }
/* Photos */
.panel-nested { padding: .75rem; display: grid; gap: .6rem; }
.photos-grid { display: grid; gap: .65rem; grid-template-columns: repeat(1, minmax(0, 1fr)); }
.photo-card { border: 1px solid var(--cds-border-card); border-radius: var(--cds-radius-md); background: var(--cds-white); overflow: hidden; }
.photo-card img { width: 100%; height: 180px; object-fit: cover; display: block; }
.photo-meta { padding: .6rem; display: grid; gap: .2rem; font-size: var(--cds-text-sm); }
/* Notes */
.notes-list { display: grid; gap: .5rem; }
.note-card { border: 1px solid var(--cds-border-card); border-radius: var(--cds-radius-md); background: var(--cds-white); padding: .65rem; display: grid; gap: .35rem; }
.note-card header { display: flex; justify-content: space-between; gap: .45rem; }
.note-card p { margin: 0; white-space: pre-wrap; }
.note-internal { border-left: 4px solid var(--cds-light-6); }
.note-public { border-left: 4px solid var(--cds-info); }
.note-technical { border-left: 4px solid var(--cds-warning-text); }
@media (min-width: 900px) {
  .summary-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .detail-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .photos-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
</style>
