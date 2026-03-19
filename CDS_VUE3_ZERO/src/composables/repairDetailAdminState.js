import {
  baseRepairDetailEditForm,
  buildFallbackRepairStatusOption
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
    warranty: payload?.warranty || null,
    invoice: payload?.invoice || null,
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

export function mergeRepairStatusCatalog(statusOptions, repair) {
  const catalog = Array.isArray(statusOptions) ? [...statusOptions] : []
  const fallbackOption = buildFallbackRepairStatusOption(repair)
  if (!fallbackOption) return catalog

  const alreadyPresent = catalog.some((option) => option?.id === fallbackOption.id)
  if (!alreadyPresent) {
    catalog.push(fallbackOption)
  }
  return catalog.sort((a, b) => Number(a?.id || 0) - Number(b?.id || 0))
}

export function buildRepairDetailVisibleStatusOptions(statusCatalog, repair) {
  const catalog = mergeRepairStatusCatalog(statusCatalog, repair)
  const allowedIds = Array.isArray(repair?.allowed_status_ids)
    ? repair.allowed_status_ids.map((value) => Number(value || 0)).filter((value) => value > 0)
    : []

  if (!allowedIds.length) return catalog

  const visible = new Set(allowedIds)
  return catalog.filter((option) => visible.has(Number(option?.id || 0)))
}

export function resolveRepairStatusLabel(repair, statusOptions = []) {
  const match = mergeRepairStatusCatalog(statusOptions, repair)
    .find((option) => option.id === Number(repair?.status_id || 0))
  return match?.label || String(repair?.status || 'Sin estado')
}

export function resolveRepairStatusClass(repair) {
  const statusCode = String(repair?.status_code || '').trim().toLowerCase()
  if (['ingreso', 'diagnostico', 'presupuesto'].includes(statusCode)) return 'status-pending'
  if (['aprobado', 'en_trabajo', 'listo'].includes(statusCode)) return 'status-progress'
  if (['entregado', 'noventena'].includes(statusCode)) return 'status-success'
  if (statusCode === 'archivado') return 'status-archived'
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
