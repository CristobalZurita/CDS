const STATUS_ALIASES = {
  pending: 'ingreso',
  pending_quote: 'ingreso',
  quoted: 'presupuesto',
  approved: 'aprobado',
  in_progress: 'en_trabajo',
  'in-progress': 'en_trabajo',
  waiting_parts: 'en_trabajo',
  waiting: 'en_trabajo',
  testing: 'listo',
  completed: 'entregado',
  delivered: 'entregado',
  cancelled: 'rechazado',
  ingreso: 'ingreso',
  diagnostico: 'diagnostico',
  presupuesto: 'presupuesto',
  aprobado: 'aprobado',
  en_trabajo: 'en_trabajo',
  listo: 'listo',
  entregado: 'entregado',
  noventena: 'noventena',
  archivado: 'archivado',
  rechazado: 'rechazado'
}

const STATUS_LABELS = {
  ingreso: 'Ingreso',
  diagnostico: 'Diagnostico',
  presupuesto: 'Presupuesto',
  aprobado: 'Aprobado',
  en_trabajo: 'En trabajo',
  listo: 'Listo',
  entregado: 'Entregado',
  noventena: 'Noventena',
  archivado: 'Archivado',
  rechazado: 'Rechazado'
}

const STATUS_PROGRESS = {
  ingreso: 10,
  diagnostico: 20,
  presupuesto: 30,
  aprobado: 40,
  en_trabajo: 60,
  listo: 80,
  entregado: 100,
  noventena: 100,
  archivado: 100,
  rechazado: 0
}

export function normalizeRepairStatus(status) {
  const key = String(status || '').trim().toLowerCase()
  return STATUS_ALIASES[key] || (key || 'ingreso')
}

export function getRepairStatusLabel(status) {
  const normalized = normalizeRepairStatus(status)
  return STATUS_LABELS[normalized] || normalized
}

export function getRepairProgressByStatus(status) {
  const normalized = normalizeRepairStatus(status)
  return STATUS_PROGRESS[normalized] ?? 10
}

export function getRepairStatusBucket(status) {
  const normalized = normalizeRepairStatus(status)
  if (normalized === 'rechazado') return 'cancelled'
  if (['entregado', 'noventena', 'archivado'].includes(normalized)) return 'completed'
  if (['aprobado', 'en_trabajo', 'listo'].includes(normalized)) return 'in_progress'
  return 'pending_quote'
}

export function isActiveRepairStatus(status) {
  const normalized = normalizeRepairStatus(status)
  return ['aprobado', 'en_trabajo', 'listo'].includes(normalized)
}
