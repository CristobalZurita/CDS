import { computed, reactive } from 'vue'

export const smdCapacitorTypeOptions = [
  { value: 'EIA3', label: 'EIA-3' },
  { value: 'EIA4', label: 'EIA-4' },
  { value: 'EIA198', label: 'EIA-198' }
]

function decodeSmdCapacitor(code, type) {
  const normalized = String(code || '').trim().toUpperCase()
  if (!normalized) return Number.NaN

  let valuePf = Number.NaN
  if ((type === 'EIA3' || type === 'EIA198') && normalized.length === 3) {
    const sig = Number(normalized.slice(0, 2))
    const mult = Math.pow(10, Number(normalized[2]))
    valuePf = sig * mult
  } else if (type === 'EIA4' && normalized.length === 4) {
    const sig = Number(normalized.slice(0, 3))
    const mult = Math.pow(10, Number(normalized[3]))
    valuePf = sig * mult
  }

  return valuePf
}

function normalize(value) {
  if (!Number.isFinite(value)) return null
  return Number(value.toFixed(6))
}

export function useSmdCapacitorCalculator() {
  const form = reactive({
    code: '',
    type: 'EIA3',
    pf: null,
    nf: null,
    uf: null,
    f: null
  })

  const decodedPf = computed(() => decodeSmdCapacitor(form.code, form.type))
  const isValidCode = computed(() => Number.isFinite(decodedPf.value))

  const decoded = computed(() => {
    if (!isValidCode.value) {
      return { pf: null, nf: null, uf: null }
    }
    return {
      pf: normalize(decodedPf.value),
      nf: normalize(decodedPf.value / 1000),
      uf: normalize(decodedPf.value / 1000000)
    }
  })

  function convertFrom(field) {
    const value = Number(form[field])
    if (!Number.isFinite(value)) {
      form.pf = null
      form.nf = null
      form.uf = null
      form.f = null
      return
    }

    let pf = value
    if (field === 'nf') pf = value * 1000
    if (field === 'uf') pf = value * 1000000
    if (field === 'f') pf = value * 1000000000000

    form.pf = normalize(pf)
    form.nf = normalize(pf / 1000)
    form.uf = normalize(pf / 1000000)
    form.f = normalize(pf / 1000000000000)
  }

  function resetConversion() {
    form.pf = null
    form.nf = null
    form.uf = null
    form.f = null
  }

  function resetCode() {
    form.code = ''
    form.type = 'EIA3'
  }

  return {
    form,
    decoded,
    isValidCode,
    convertFrom,
    resetCode,
    resetConversion
  }
}
