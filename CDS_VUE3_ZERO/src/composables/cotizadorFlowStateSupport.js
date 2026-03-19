export function createCotizadorLeadForm() {
  return { nombre: '', email: '', telefono: '' }
}

export function formatCotizadorCost(value) {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(Number(value || 0))
}

function clearCotizadorModelState(state) {
  state.selectedModel.value = ''
  state.models.value = []
  state.faults.value = []
  state.selectedFaultIds.value = []
}

export function resetCotizadorQuoteTurnstile(state) {
  state.quoteTurnstileToken.value = ''
  state.quoteTurnstileRenderKey.value += 1
}

export function resetCotizadorLeadTurnstile(state) {
  state.leadTurnstileToken.value = ''
  state.leadTurnstileRenderKey.value += 1
}

function resetCotizadorTurnstiles(state) {
  resetCotizadorQuoteTurnstile(state)
  resetCotizadorLeadTurnstile(state)
}

export function setCotizadorBrandSelection(state, brandId) {
  state.selectedBrand.value = brandId
  clearCotizadorModelState(state)
  if (!brandId) return
  resetCotizadorTurnstiles(state)
}

export function setCotizadorModelSelection(state, instrumentId) {
  state.selectedModel.value = instrumentId
  state.faults.value = []
  state.selectedFaultIds.value = []
  if (!instrumentId) return
  resetCotizadorTurnstiles(state)
}

export function toggleCotizadorFaultSelection(state, faultId) {
  const idx = state.selectedFaultIds.value.indexOf(faultId)
  state.selectedFaultIds.value = idx === -1
    ? [...state.selectedFaultIds.value, faultId]
    : state.selectedFaultIds.value.filter((id) => id !== faultId)
  resetCotizadorTurnstiles(state)
}

export function activateCotizadorNotFoundMode(state) {
  state.notFoundMode.value = true
  state.selectedBrand.value = ''
  clearCotizadorModelState(state)
  resetCotizadorTurnstiles(state)
}

export function deactivateCotizadorNotFoundMode(state) {
  state.notFoundMode.value = false
  state.manualBrand.value = ''
  state.manualModel.value = ''
  resetCotizadorTurnstiles(state)
}

export function resetCotizadorFlowState(state) {
  state.step.value = 1
  state.selectedBrand.value = ''
  clearCotizadorModelState(state)
  state.quoteResult.value = null
  state.leadForm.value = createCotizadorLeadForm()
  state.acceptedDisclaimer.value = false
  state.quoteTurnstileToken.value = ''
  state.quoteTurnstileRenderKey.value = 0
  state.leadTurnstileToken.value = ''
  state.leadTurnstileRenderKey.value = 0
  state.leadSubmitted.value = false
  state.notFoundMode.value = false
  state.manualBrand.value = ''
  state.manualModel.value = ''
}
