import { ref, computed } from 'vue'
import brandsData from '@/assets/data/brands.json'
import instrumentsData from '@/assets/data/instruments.json'
import faultsData from '@/assets/data/faults.json'

export function useDiagnostic() {
  // State
  const selectedBrand = ref(null)
  const selectedModel = ref(null)
  const selectedFaults = ref([])
  const clientName = ref('')
  const clientEmail = ref('')
  const clientPhone = ref('')
  const equipmentValue = ref(null)

  // Data
  const brands = computed(() => brandsData.brands)
  const instruments = computed(() => instrumentsData.instruments)
  const faults = computed(() => faultsData.faults)

  /**
   * Get all available brands
   */
  const getBrands = () => brands.value

  /**
   * Get models for a specific brand
   */
  const getModelsByBrand = (brandId) => {
    return instruments.value.filter(item => item.brand === brandId)
  }

  /**
   * Get a specific instrument details
   */
  const getInstrument = (instrumentId) => {
    return instruments.value.find(item => item.id === instrumentId)
  }

  /**
   * Get brand details
   */
  const getBrand = (brandId) => {
    return brands.value.find(item => item.id === brandId)
  }

  /**
   * Get applicable components for an instrument
   */
  const getApplicableComponents = (instrumentId) => {
    const instrument = getInstrument(instrumentId)
    if (!instrument) return []

    const applicableComponents = []

    // Keyboard components
    if (instrument.components.faders > 0) {
      applicableComponents.push({
        type: 'faders',
        count: instrument.components.faders,
        faultIds: ['FADER_INTERMITTENT']
      })
    }

    if (instrument.components.encoders_rotativos > 0) {
      applicableComponents.push({
        type: 'encoders',
        count: instrument.components.encoders_rotativos,
        faultIds: ['ENCODER_INTERMITTENT']
      })
    }

    if (instrument.components.botones > 0) {
      applicableComponents.push({
        type: 'buttons',
        count: instrument.components.botones,
        faultIds: ['BUTTON_STUCK', 'BUTTON_DEAD']
      })
    }

    // Keyboard
    if (instrument.type.toLowerCase().includes('teclado')) {
      applicableComponents.push({
        type: 'keyboard',
        faultIds: ['KEYBOARD_DEAD_KEY', 'KEYBOARD_STUCK_KEY', 'AFTERTOUCH_BROKEN']
      })
    }

    // LCD
    if (instrument.components.lcd) {
      applicableComponents.push({
        type: 'lcd',
        faultIds: ['LCD_DEAD', 'LCD_LOW_CONTRAST']
      })
    }

    // Connectivity
    if (instrument.components.usb) {
      applicableComponents.push({
        type: 'usb',
        faultIds: ['USB_NOT_RECOGNIZED']
      })
    }

    if (instrument.components.midi_din) {
      applicableComponents.push({
        type: 'midi',
        faultIds: ['MIDI_NOT_RECOGNIZED']
      })
    }

    // Wheels
    if (instrument.components.rueda_pitch) {
      applicableComponents.push({
        type: 'pitch_wheel',
        faultIds: ['PITCH_WHEEL_BROKEN']
      })
    }

    return applicableComponents
  }

  /**
   * Get available faults for current selection
   */
  const getAvailableFaults = () => {
    if (!selectedModel.value) return Object.values(faults.value)

    const instrument = getInstrument(selectedModel.value)
    if (!instrument) return Object.values(faults.value)

    // Get faults specific to this instrument type
    const applicableComponents = getApplicableComponents(selectedModel.value)
    const applicableFaultIds = new Set()

    // Add all applicable faults from components
    applicableComponents.forEach(component => {
      component.faultIds.forEach(faultId => {
        applicableFaultIds.add(faultId)
      })
    })

    // Always add general faults
    applicableFaultIds.add('POWER')
    applicableFaultIds.add('POWER_UNSTABLE')
    applicableFaultIds.add('AUDIO_DISTORTED')
    applicableFaultIds.add('AUDIO_NO_OUTPUT')
    applicableFaultIds.add('AUDIO_WEAK')
    applicableFaultIds.add('COSMETIC_DAMAGE')
    applicableFaultIds.add('WATER_DAMAGE')
    applicableFaultIds.add('CAPACITOR_BLOWN')
    applicableFaultIds.add('CONNECTOR_LOOSE')

    return Array.from(applicableFaultIds)
      .map(faultId => faults.value[faultId])
      .filter(fault => fault)
  }

  /**
   * Add a fault to the selection
   */
  const addFault = (faultId) => {
    const fault = faults.value[faultId]
    if (!fault) return

    // Check for precedence faults
    if (fault.isPrecedence) {
      selectedFaults.value = [faultId]
    } else {
      // Check if any precedence fault is already selected
      const hasPrecedence = selectedFaults.value.some(id => faults.value[id]?.isPrecedence)

      if (!hasPrecedence && !selectedFaults.value.includes(faultId)) {
        selectedFaults.value.push(faultId)
      }
    }
  }

  /**
   * Remove a fault from the selection
   */
  const removeFault = (faultId) => {
    selectedFaults.value = selectedFaults.value.filter(id => id !== faultId)
  }

  /**
   * Clear all selected faults
   */
  const clearFaults = () => {
    selectedFaults.value = []
  }

  /**
   * Get effective faults (considering precedence rules)
   */
  const getEffectiveFaults = () => {
    // Check for precedence faults
    const precedenceFault = selectedFaults.value.find(id => faults.value[id]?.isPrecedence)

    if (precedenceFault) {
      return [precedenceFault]
    }

    return selectedFaults.value
  }

  /**
   * Calculate quote based on faults and equipment value
   */
  const calculateQuote = () => {
    if (!selectedModel.value || selectedFaults.value.length === 0) {
      return null
    }

    const instrument = getInstrument(selectedModel.value)
    if (!instrument) return null

    const effectiveFaults = getEffectiveFaults()
    let totalPrice = 0

    // Sum base prices
    effectiveFaults.forEach(faultId => {
      const fault = faults.value[faultId]
      if (fault) {
        totalPrice += fault.basePrice
      }
    })

    // Apply complexity factor based on equipment tier
    let complexityFactor = 1.0
    const tier = getBrand(selectedBrand.value)?.tier

    const complexityFactors = {
      legendary: 1.8,
      professional: 1.5,
      standard: 1.2,
      specialized: 1.3,
      boutique: 1.4,
      historic: 1.3
    }

    complexityFactor = complexityFactors[tier] || 1.0

    // Apply equipment value factor
    let valueFactor = 1.0
    const estValue = instrument.valor_estimado

    if (estValue) {
      const minValue = estValue.min
      if (minValue > 5000000) {
        valueFactor = 2.0
      } else if (minValue > 2000000) {
        valueFactor = 1.6
      } else if (minValue > 500000) {
        valueFactor = 1.3
      }
    }

    // Calculate final price with multipliers
    const finalPrice = Math.round(totalPrice * complexityFactor * valueFactor)

    return {
      baseCost: totalPrice,
      complexityFactor,
      valueFactor,
      finalCost: finalPrice,
      instrument,
      brand: getBrand(selectedBrand.value),
      faults: effectiveFaults.map(id => faults.value[id])
    }
  }

  /**
   * Validate name: Letters (including accents) and spaces, 2-50 chars
   */
  const validateName = (name) => {
    if (!name) return false
    return /^[A-Za-zÀ-ÿ\s]{2,50}$/.test(name.trim())
  }

  /**
   * Validate email: Standard email format
   */
  const validateEmail = (email) => {
    if (!email) return false
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email.trim())
  }

  /**
   * Validate phone: Optional, but if provided must be 8-15 digits with optional +
   */
  const validatePhone = (phone) => {
    if (!phone) return true // Phone is optional
    return /^\+?[0-9]{8,15}$/.test(phone.trim().replace(/\s/g, ''))
  }

  /**
   * Validate current selection
   */
  const isValid = () => {
    return (
      selectedBrand.value &&
      selectedModel.value &&
      selectedFaults.value.length > 0 &&
      validateName(clientName.value) &&
      validateEmail(clientEmail.value) &&
      validatePhone(clientPhone.value)
    )
  }

  /**
   * Reset the form
   */
  const reset = () => {
    selectedBrand.value = null
    selectedModel.value = null
    selectedFaults.value = []
    clientName.value = ''
    clientEmail.value = ''
    clientPhone.value = ''
    equipmentValue.value = null
  }

  /**
   * Get quote data for submission
   */
  const getQuoteData = () => {
    const quote = calculateQuote()

    return {
      client: {
        name: clientName.value,
        email: clientEmail.value,
        phone: clientPhone.value
      },
      equipment: {
        brand: selectedBrand.value,
        model: selectedModel.value,
        estimatedValue: equipmentValue.value
      },
      diagnostics: {
        faults: getEffectiveFaults(),
        quote
      },
      timestamp: new Date().toISOString()
    }
  }

  return {
    // State
    selectedBrand,
    selectedModel,
    selectedFaults,
    clientName,
    clientEmail,
    clientPhone,
    equipmentValue,

    // Data
    brands,
    instruments,
    faults,

    // Methods
    getBrands,
    getModelsByBrand,
    getInstrument,
    getBrand,
    getApplicableComponents,
    getAvailableFaults,
    addFault,
    removeFault,
    clearFaults,
    getEffectiveFaults,
    calculateQuote,
    isValid,
    validateName,
    validateEmail,
    validatePhone,
    reset,
    getQuoteData
  }
}
