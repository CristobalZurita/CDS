import {
  baseRepairDetailEditForm,
  REPAIR_DETAIL_STATUS_OPTIONS
} from '@/services/repairDetailAdminService'
import { extractErrorMessage } from '@/services/api'

export function buildRepairDetailEditDraft(repair) {
  if (!repair) return baseRepairDetailEditForm()
  return {
    diagnosis: String(repair.diagnosis || ''),
    work_performed: String(repair.work_performed || ''),
    parts_cost: Number(repair.parts_cost || 0),
    labor_cost: Number(repair.labor_cost || 0),
    additional_cost: Number(repair.additional_cost || 0),
    discount: Number(repair.discount || 0),
    total_cost: Number(repair.total_cost || 0),
    paid_amount: Number(repair.paid_amount || 0),
    payment_method: String(repair.payment_method || 'cash')
  }
}

export function buildRepairDetailScreenDrafts(repair) {
  return {
    statusDraft: Number(repair?.status_id || 1),
    editForm: buildRepairDetailEditDraft(repair)
  }
}

export function buildRepairDetailBundleState(payload) {
  const repair = payload?.repair || null
  return {
    repair,
    photos: Array.isArray(payload?.photos) ? payload.photos : [],
    notes: Array.isArray(payload?.notes) ? payload.notes : [],
    ...buildRepairDetailScreenDrafts(repair)
  }
}

export function createPhotoDraft() {
  return {
    file: null,
    caption: '',
    type: 'general',
    open: false
  }
}

export function toggleRepairPhotoDraft(photoDraft) {
  return {
    ...photoDraft,
    open: !photoDraft?.open
  }
}

export function updateRepairPhotoDraft(photoDraft, payload) {
  const nextDraft = {
    ...photoDraft
  }

  if (payload?.field === 'newPhotoCaption') {
    nextDraft.caption = payload.value
  }

  if (payload?.field === 'newPhotoType') {
    nextDraft.type = payload.value
  }

  return nextDraft
}

export function setRepairPhotoDraftFile(photoDraft, event) {
  return {
    ...photoDraft,
    file: event?.target?.files?.[0] || null
  }
}

export function createNoteDraft() {
  return {
    text: '',
    type: 'internal',
    open: false
  }
}

export function toggleRepairNoteDraft(noteDraft) {
  return {
    ...noteDraft,
    open: !noteDraft?.open
  }
}

export function updateRepairNoteDraft(noteDraft, payload) {
  const nextDraft = {
    ...noteDraft
  }

  if (payload?.field === 'newNote') {
    nextDraft.text = payload.value
  }

  if (payload?.field === 'newNoteType') {
    nextDraft.type = payload.value
  }

  return nextDraft
}

export function resolveRepairNoteSubmission(noteDraft) {
  const note = String(noteDraft?.text || '').trim()
  return {
    note,
    noteType: String(noteDraft?.type || 'internal'),
    isValid: Boolean(note),
    error: note ? '' : 'La nota no puede estar vacia.'
  }
}

export function resolveRepairStatusLabel(repair) {
  const match = REPAIR_DETAIL_STATUS_OPTIONS.find((option) => option.id === Number(repair?.status_id || 0))
  return match?.label || String(repair?.status || 'Sin estado')
}

export function resolveRepairStatusClass(repair) {
  const statusId = Number(repair?.status_id || 0)
  if ([1, 2, 3].includes(statusId)) return 'status-pending'
  if ([4, 5, 6].includes(statusId)) return 'status-progress'
  if ([7, 8].includes(statusId)) return 'status-success'
  if (statusId === 9) return 'status-archived'
  return 'status-neutral'
}

export function resolveRepairPriorityLabel(repair) {
  const priority = Number(repair?.priority || 2)
  if (priority === 1) return 'Alta'
  if (priority === 3) return 'Baja'
  return 'Normal'
}

export function resolveRepairPriorityClass(repair) {
  const priority = Number(repair?.priority || 2)
  if (priority === 1) return 'priority-high'
  if (priority === 3) return 'priority-low'
  return 'priority-normal'
}

export async function runRepairDetailTask(flagRef, errorRef, task, { resolveError = extractErrorMessage } = {}) {
  flagRef.value = true
  errorRef.value = ''

  try {
    return await task()
  } catch (requestError) {
    errorRef.value = resolveError(requestError)
    return null
  } finally {
    flagRef.value = false
  }
}

export async function runRepairDetailReloadTask(
  flagRef,
  errorRef,
  task,
  reloadTask,
  options = {}
) {
  const result = await runRepairDetailTask(flagRef, errorRef, task, options)
  if (errorRef.value) return result
  await reloadTask()
  return result
}

export async function runRepairDetailSuccessTask(
  flagRef,
  errorRef,
  task,
  { onSuccess, ...options } = {}
) {
  const result = await runRepairDetailTask(flagRef, errorRef, task, options)
  if (errorRef.value) return result
  onSuccess?.(result)
  return result
}
