import { ref, computed } from 'vue'
import brandsData from '@/assets/data/brands.json'
import instrumentsData from '@/assets/data/instruments.json'
import faultsData from '@/assets/data/faults.json'
import type { ComputedRef, Ref } from 'vue'

interface Brand {
  id: string
  name: string
  tier?: string
  [key: string]: any
}

interface Instrument {
  id: string
  brand: string
  model: string
  type: string
  year?: number
  components: {
    faders?: number
    encoders_rotativos?: number
    botones?: number
    lcd?: boolean
    usb?: boolean
    midi_din?: boolean
    rueda_pitch?: boolean
    [key: string]: any
  }
  valor_estimado?: {
    min: number
    max: number
  }
  [key: string]: any
}

interface Fault {
  id: string
  name: string
  basePrice: number
  isPrecedence?: boolean
  [key: string]: any
}

interface ApplicableComponent {
  type: string
  count?: number
  faultIds: string[]
}

interface QuoteResult {
  baseCost: number
  complexityFactor: number
  valueFactor: number
  finalCost: number
  instrument: Instrument
  brand: Brand | undefined
  faults: Fault[]
}

interface QuoteData {
  client: {
    name: string
    email: string
    phone: string
  }
  equipment: {
    brand: string
    model: string
    estimatedValue: number | null
  }
  diagnostics: {
    faults: string[]
    quote: QuoteResult | null
  }
  timestamp: string
}

export interface UseDiagnosticComposable {
  // State
  selectedBrand: Ref<string | null>
  selectedModel: Ref<string | null>
  selectedFaults: Ref<string[]>
  clientName: Ref<string>
  clientEmail: Ref<string>
  clientPhone: Ref<string>
  equipmentValue: Ref<number | null>

  // Data
  brands: ComputedRef<Brand[]>
  instruments: ComputedRef<Instrument[]>
  faults: ComputedRef<{ [key: string]: Fault }>

  // Methods
  getBrands: () => Brand[]
  getModelsByBrand: (brandId: string) => Instrument[]
  getInstrument: (instrumentId: string) => Instrument | undefined
  getBrand: (brandId: string) => Brand | undefined
  getApplicableComponents: (instrumentId: string) => ApplicableComponent[]
  getAvailableFaults: () => Fault[]
  addFault: (faultId: string) => void
  removeFault: (faultId: string) => void
  clearFaults: () => void
  getEffectiveFaults: () => string[]
  calculateQuote: () => QuoteResult | null
  isValid: () => boolean
  validateName: (name: string) => boolean
  validateEmail: (email: string) => boolean
  validatePhone: (phone: string) => boolean
  reset: () => void
  getQuoteData: () => QuoteData
}

export function useDiagnostic(): UseDiagnosticComposable {
  // State
  const selectedBrand = ref<string | null>(null)
  const selectedModel = ref<string | null>(null)
  const selectedFaults = ref<string[]>([])
  const clientName = ref('')
  const clientEmail = ref('')
  const clientPhone = ref('')
  const equipmentValue = ref<number | null>(null)

  // Data
  const brands = computed(() => brandsData.brands as Brand[])
  const instruments = computed(() => instrumentsData.instruments as Instrument[])
  const faults = computed(() => faultsData.faults as { [key: string]: Fault })

  /**
   * Get all available brands
   */
  const getBrands = (): Brand[] => brands.value

  /**
   * Get models for a specific brand
   */
  const getModelsByBrand = (brandId: string): Instrument[] => {
    return instruments.value.filter(item => item.brand === brandId)
  }

  /**
   * Get a specific instrument details
   */
  const getInstrument = (instrumentId: string): Instrument | undefined => {
    return instruments.value.find(item => item.id === instrumentId)
  }

  /**
   * Get brand details
   */
  const getBrand = (brandId: string): Brand | undefined => {
    return brands.value.find(item => item.id === brandId)
  }

  /**
   * Get applicable components for an instrument
   */
  const getApplicableComponents = (instrumentId: string): ApplicableComponent[] => {
    const instrument = getInstrument(instrumentId)
    if (!instrument) return []

    const applicableComponents: ApplicableComponent[] = []

    // Keyboard components
    if (instrument.components.faders && instrument.components.faders > 0) {
      applicableComponents.push({
        type: 'faders',
        count: instrument.components.faders,
        faultIds: ['FADER_INTERMITTENT']
      })
    }

    if (instrument.components.encoders_rotativos && instrument.components.encoders_rotativos > 0) {
      applicableComponents.push({
        type: 'encoders',
        count: instrument.components.encoders_rotativos,
        faultIds: ['ENCODER_INTERMITTENT']
      })
    }

    if (instrument.components.botones && instrument.components.botones > 0) {
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
  const getAvailableFaults = (): Fault[] => {
    if (!selectedModel.value) return Object.values(faults.value)

    const instrument = getInstrument(selectedModel.value)
    if (!instrument) return Object.values(faults.value)

    // Get faults specific to this instrument type
    const applicableComponents = getApplicableComponents(selectedModel.value)
    const applicableFaultIds = new Set<string>()

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
      .filter((fault): fault is Fault => fault !== undefined)
  }

  /**
   * Add a fault to the selection
   */
  const addFault = (faultId: string): void => {
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
  const removeFault = (faultId: string): void => {
    selectedFaults.value = selectedFaults.value.filter(id => id !== faultId)
  }

  /**
   * Clear all selected faults
   */
  const clearFaults = (): void => {
    selectedFaults.value = []
  }

  /**
   * Get effective faults (considering precedence rules)
   */
  const getEffectiveFaults = (): string[] => {
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
  const calculateQuote = (): QuoteResult | null => {
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
    const tier = getBrand(selectedBrand.value || '')?.tier as string

    const complexityFactors: { [key: string]: number } = {
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
      brand: getBrand(selectedBrand.value || ''),
      faults: effectiveFaults.map(id => faults.value[id]).filter((f): f is Fault => f !== undefined)
    }
  }

  /**
   * Validate name: Letters (including accents) and spaces, 2-50 chars
   */
  const validateName = (name: string): boolean => {
    if (!name) return false
    return /^[A-Za-zÀ-ÿ\s]{2,50}$/.test(name.trim())
  }

  /**
   * Validate email: Standard email format
   */
  const validateEmail = (email: string): boolean => {
    if (!email) return false
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email.trim())
  }

  /**
   * Validate phone: Optional, but if provided must be 8-15 digits with optional +
   */
  const validatePhone = (phone: string): boolean => {
    if (!phone) return true // Phone is optional
    return /^\+?[0-9]{8,15}$/.test(phone.trim().replace(/\s/g, ''))
  }

  /**
   * Validate current selection
   */
  const isValid = (): boolean => {
    return (
      !!selectedBrand.value &&
      !!selectedModel.value &&
      selectedFaults.value.length > 0 &&
      validateName(clientName.value) &&
      validateEmail(clientEmail.value) &&
      validatePhone(clientPhone.value)
    )
  }

  /**
   * Reset the form
   */
  const reset = (): void => {
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
  const getQuoteData = (): QuoteData => {
    const quote = calculateQuote()

    return {
      client: {
        name: clientName.value,
        email: clientEmail.value,
        phone: clientPhone.value
      },
      equipment: {
        brand: selectedBrand.value || '',
        model: selectedModel.value || '',
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
