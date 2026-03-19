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

      <RepairDetailSummaryCards
        :repair="repair"
        :status-label="statusLabel"
        :status-class="statusClass"
        :priority-label="priorityLabel"
        :priority-class="priorityClass"
        :format-currency="formatCurrency"
      />

      <RepairDetailInfoPanel
        :repair="repair"
        :is-archived="isArchived"
      />

      <RepairDetailTechnicalPanel
        :status-options="statusOptions"
        :status-draft="statusDraft"
        :edit-form="editForm"
        :updating-status="updatingStatus"
        :saving-repair="savingRepair"
        @update-status-draft="statusDraft = $event"
        @update-edit-field="updateEditField"
        @update-status="updateStatus"
        @save-repair-fields="saveRepairFields"
      />

      <RepairDetailSignaturePanel
        :repair="repair"
        :performing-action="performingAction"
        :signature-link="signatureLink"
        :photo-upload-link="photoUploadLink"
        @request-signature="requestSignature"
        @request-photo-upload="requestPhotoUpload"
      />

      <RepairDetailPhotosPanel
        :photos="photos"
        :show-photo-upload="showPhotoUpload"
        :selected-file="selectedFile"
        :new-photo-caption="newPhotoCaption"
        :new-photo-type="newPhotoType"
        :uploading-photo="uploadingPhoto"
        :format-date="formatDate"
        @toggle-upload="togglePhotoUpload"
        @file-selected="onFileSelected"
        @update-photo-field="updatePhotoField"
        @upload-photo="uploadPhoto"
      />

      <RepairDetailNotesPanel
        :notes="notes"
        :show-note-form="showNoteForm"
        :new-note="newNote"
        :new-note-type="newNoteType"
        :saving-note="savingNote"
        :note-type-class="noteTypeClass"
        :format-date="formatDate"
        @toggle-note-form="toggleNoteForm"
        @update-note-field="updateNoteField"
        @add-note="addNote"
      />

      <RepairDetailActionsPanel
        :performing-action="performingAction"
        :downloading-closure-pdf="downloadingClosurePdf"
        :is-archived="isArchived"
        @notify-client="notifyClient"
        @download-closure-pdf="downloadClosurePdf"
        @archive-repair="archiveRepair"
        @reactivate-repair="reactivateRepair"
      />
    </template>
  </main>
</template>

<script setup>
import RepairDetailActionsPanel from '@/components/admin/RepairDetailActionsPanel.vue'
import RepairDetailInfoPanel from '@/components/admin/RepairDetailInfoPanel.vue'
import RepairDetailNotesPanel from '@/components/admin/RepairDetailNotesPanel.vue'
import RepairDetailPhotosPanel from '@/components/admin/RepairDetailPhotosPanel.vue'
import RepairDetailSignaturePanel from '@/components/admin/RepairDetailSignaturePanel.vue'
import RepairDetailSummaryCards from '@/components/admin/RepairDetailSummaryCards.vue'
import RepairDetailTechnicalPanel from '@/components/admin/RepairDetailTechnicalPanel.vue'
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
  updateEditField,
  togglePhotoUpload,
  onFileSelected,
  updatePhotoField,
  uploadPhoto,
  toggleNoteForm,
  updateNoteField,
  addNote,
  downloadClosurePdf,
  goToPurchaseRequests,
  goBack
} = useRepairDetailAdminPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped src="./repairDetailAdminShared.css"></style>
