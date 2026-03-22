/**
 * usePlacesAutocomplete
 * =====================
 * Lazy-loads the Google Maps Places API and attaches autocomplete to an input.
 *
 * Requires VITE_GOOGLE_MAPS_API_KEY in the environment.
 * Degrades gracefully: if the key is absent the input stays a plain text field.
 *
 * Usage:
 *   const { initAutocomplete } = usePlacesAutocomplete()
 *
 *   // inside onMounted:
 *   const cleanup = await initAutocomplete(inputEl, ({ address, city, region, country }) => {
 *     form.address = address
 *     form.city    = city
 *     form.region  = region
 *   })
 *   onUnmounted(cleanup)
 */

let _scriptPromise = null

function _loadGoogleMapsScript(apiKey) {
  if (_scriptPromise) return _scriptPromise
  if (window.google?.maps?.places) {
    _scriptPromise = Promise.resolve()
    return _scriptPromise
  }
  _scriptPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&loading=async`
    script.async = true
    script.defer = true
    script.onload = resolve
    script.onerror = () => {
      _scriptPromise = null  // allow retry
      reject(new Error('Google Maps script failed to load'))
    }
    document.head.appendChild(script)
  })
  return _scriptPromise
}

/**
 * @param {HTMLInputElement} inputEl
 * @param {Function} onPlace  — called with { address, city, region, country, lat, lng }
 * @param {Object}   [opts]   — google.maps.places.Autocomplete options override
 * @returns {Promise<Function>} — async cleanup function
 */
async function initAutocomplete(inputEl, onPlace, opts = {}) {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY
  if (!apiKey || !inputEl) return () => {}

  try {
    await _loadGoogleMapsScript(apiKey)
  } catch {
    return () => {}
  }

  const options = {
    componentRestrictions: { 
      country: import.meta.env.VITE_GOOGLE_MAPS_COUNTRY || 'cl' 
    },
    fields: ['formatted_address', 'address_components', 'geometry'],
    ...opts,
  }

  const ac = new window.google.maps.places.Autocomplete(inputEl, options)

  const listener = ac.addListener('place_changed', () => {
    const place = ac.getPlace()
    if (!place?.address_components) return

    let city = ''
    let region = ''
    let country = 'Chile'

    for (const comp of place.address_components) {
      const types = comp.types || []
      if (types.includes('locality')) city = comp.long_name
      else if (types.includes('administrative_area_level_2') && !city) city = comp.long_name
      else if (types.includes('administrative_area_level_1')) region = comp.long_name
      else if (types.includes('country')) country = comp.long_name
    }

    onPlace({
      address: place.formatted_address || '',
      city,
      region,
      country,
      lat: place.geometry?.location?.lat() ?? null,
      lng: place.geometry?.location?.lng() ?? null,
    })
  })

  return () => {
    try {
      window.google?.maps?.event?.removeListener(listener)
    } catch { /* ignore */ }
  }
}

export function usePlacesAutocomplete() {
  return { initAutocomplete }
}
