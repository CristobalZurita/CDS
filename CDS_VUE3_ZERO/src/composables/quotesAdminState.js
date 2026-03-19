export function createEmptyQuotesBoard() {
  return { draft_pending: [], waiting_response: [], closed: [] }
}

export function createEmptyQuotesCounts() {
  return { draft_pending: 0, waiting_response: 0, closed: 0, total: 0 }
}

export function createEmptyQuotesMetrics() {
  return { pending: 0, sent: 0, approved: 0, denied: 0, canceled: 0, expired_open: 0, expiring_3d: 0, open_total: 0 }
}

export function buildQuotesBoardState(normalized) {
  return {
    board: normalized?.board || createEmptyQuotesBoard(),
    counts: normalized?.counts || createEmptyQuotesCounts(),
    metrics: normalized?.metrics || createEmptyQuotesMetrics()
  }
}

export function setQuoteBusyState(busyIds, quoteId, value) {
  const id = Number(quoteId)
  const next = new Set(busyIds)

  if (value) {
    next.add(id)
  } else {
    next.delete(id)
  }

  return next
}

export function isQuoteBusy(busyIds, quoteId) {
  return busyIds.has(Number(quoteId))
}

export function filterQuotesBySearch(items, searchQuery) {
  const query = String(searchQuery || '').trim().toLowerCase()
  if (!query) return items

  return items.filter((quote) => {
    const text = [
      quote?.quote_number,
      quote?.client?.name,
      quote?.client_name,
      quote?.problem_description,
      quote?.status
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()

    return text.includes(query)
  })
}

export function getQuotesColumnItems(board, columnKey, searchQuery) {
  return filterQuotesBySearch(board?.[columnKey] || [], searchQuery)
}

export function resolveQuoteRepairCreationGuard(quote) {
  if (!quote?.id || !quote?.client_id) {
    return {
      isValid: false,
      error: 'No se pudo crear OT: faltan datos de cliente o cotizacion.'
    }
  }

  return {
    isValid: true,
    error: ''
  }
}

export function updateQuoteDraftField(draft, payload) {
  const field = payload?.field
  if (!field || !(field in draft)) return false
  draft[field] = payload.value
  return true
}
