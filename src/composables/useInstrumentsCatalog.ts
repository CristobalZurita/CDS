import { ref, computed } from 'vue'
import brandsData from '@/assets/data/brands.json'
import instrumentsData from '@/assets/data/instruments.json'
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
  imagen_url?: string
  image?: {
    url: string
  }
  description?: string
  [key: string]: any
}

interface EnrichedInstrument extends Instrument {
  imagePath: string
  imageVariants?: string[]
  brandLogo?: string
  displayName: string
  brandLabel: string
}

interface CatalogStats {
  totalBrands: number
  totalInstruments: number
  instrumentsWithImage: number
  coverage: number
}

export interface UseInstrumentsCatalogComposable {
  // Data refs
  brands: Ref<Brand[]>
  instruments: Ref<Instrument[]>

  // Query methods
  getBrandById: (brandId: string) => Brand | undefined
  getAllBrands: (sorted?: boolean) => Brand[]
  getInstrumentsByBrand: (brandId: string) => EnrichedInstrument[]
  getInstrumentById: (instrumentId: string) => EnrichedInstrument | null
  getInstrumentImage: (instrument: Instrument) => string
  getInstrumentImageVariants: (instrument: Instrument) => Promise<string[]>
  getBrandLogo: (brandId: string) => string
  searchInstruments: (query: string) => EnrichedInstrument[]

  // Stats
  getCatalogStats: ComputedRef<CatalogStats>
}

/**
 * useInstrumentsCatalog - Central data catalog for brands and instruments
 *
 * This composable provides:
 * - Unified access to brands and instruments from JSON (catalog ONLY)
 * - Brand → Instruments mapping
 * - Image path generation (uses static assets only, NO inventory data)
 * - Separates CATALOG (static) from INVENTORY (dynamic database)
 * 
 * NOTE: This catalog is NOT connected to inventory database.
 * Inventory photos should come from /api/v1/inventory endpoint
 */
export function useInstrumentsCatalog(): UseInstrumentsCatalogComposable {
  // Raw data
  const brands = ref<Brand[]>(brandsData.brands || [])
  const instruments = ref<Instrument[]>(instrumentsData.instruments || [])

  /**
   * Get a brand by ID
   */
  const getBrandById = (brandId: string): Brand | undefined => {
    return brands.value.find(b => b.id === brandId)
  }

  /**
   * Get all brands, optionally sorted A→Z
   */
  const getAllBrands = (sorted = true): Brand[] => {
    const list = [...brands.value]
    if (sorted) {
      return list.sort((a, b) => a.name.localeCompare(b.name))
    }
    return list
  }

  /**
   * Generate image paths for an instrument
   * Returns primary image path based on actual files in /public/images/instrumentos/
   * Pattern: /images/instrumentos/{BRAND_MODEL...}.webp (all files are WEBP format)
   */
  const getInstrumentImage = (instrument: Instrument): string => {
    // Priority 1: Use existing imagen_url if valid
    if (instrument?.imagen_url) {
      return instrument.imagen_url
    }

    // Priority 2: Generate from convention using BRAND_MODEL pattern
    if (instrument?.id && instrument?.brand && instrument?.model) {
      const brand = instrument.brand.toUpperCase()
      const model = (instrument.model || '')
        .toUpperCase()
        .replace(/\s+/g, '_')
        .replace(/[^A-Z0-9_]/g, '') // Remove special chars
      
      const brandModel = `${brand}_${model}`

      // Candidates in priority order based on actual file patterns
      // TRY VARIANTS FIRST (most likely to exist in public folder)
      const candidates = [
        // Variants with suffixes (most files have these)
        `/images/instrumentos/${brandModel}_MK1.webp`,
        `/images/instrumentos/${brandModel}_MK2.webp`,
        `/images/instrumentos/${brandModel}_XL.webp`,
        `/images/instrumentos/${brandModel}_S.webp`,
        `/images/instrumentos/${brandModel}_PLUS.webp`,
        
        // Only then try base pattern
        `/images/instrumentos/${brandModel}.webp`,
        
        // Fallback to brand logo
        `/images/instrumentos/LOGOS/LOGO_${brand}.webp`,
      ]

      // Return primary candidate (first in list)
      // Browser will fetch and display, or show placeholder if 404
      return candidates[0]
    }

    // Priority 3: Fallback placeholder
    return '/images/placeholder.svg'
  }

  /**
   * Check if an image exists by trying to load it
   * Used to build real variants list only from existing files
   */
  const imageExists = async (imagePath: string): Promise<boolean> => {
    try {
      const response = await fetch(imagePath, { method: 'HEAD' })
      return response.ok
    } catch {
      return false
    }
  }

  /**
   * Get all image variants for an instrument that ACTUALLY EXIST
   * Searches for base image and common variant suffixes
   * Returns only paths for files that are verified to exist
   * Pattern: BRAND_MODEL.webp, BRAND_MODEL_BACK.webp, etc.
   */
  const getInstrumentImageVariants = async (instrument: Instrument): Promise<string[]> => {
    if (!instrument?.id || !instrument?.brand || !instrument?.model) {
      return []
    }

    const brand = instrument.brand.toUpperCase()
    const model = (instrument.model || '')
      .toUpperCase()
      .replace(/\s+/g, '_')
      .replace(/[^A-Z0-9_]/g, '')
    
    const brandModel = `${brand}_${model}`

    // Possible variant suffixes in order of likelihood
    const suffixes = [
      '', // Base image first (e.g., BRAND_MODEL.webp)
      '_BACK',
      '_FRONT',
      '_TOP',
      '_LATERAL',
      '_SIDE',
      '_MK1',
      '_MK2',
      '_XL',
      '_S',
    ]

    // Build candidate paths
    const candidates = suffixes.map(
      suffix => `/images/instrumentos/${brandModel}${suffix}.webp`
    )

    // Test each candidate and keep only ones that exist
    const results = await Promise.all(
      candidates.map(async (path) => ({
        path,
        exists: await imageExists(path)
      }))
    )

    return results
      .filter(r => r.exists)
      .map(r => r.path)
  }

  /**
   * Get brand logo path
   * Pattern: /images/instrumentos/LOGOS/LOGO_{BRAND}.webp
   */
  const getBrandLogo = (brandId: string): string => {
    if (!brandId) return ''
    const brand = brandId.toUpperCase()
    return `/images/instrumentos/LOGOS/LOGO_${brand}.webp`
  }

  /**
   * Enrich instrument object with computed fields
   * (adds image path, formatted price, etc.)
   * Note: imageVariants are NOT included here (loaded async by component)
   */
  const enrichInstrument = (inst: Instrument): EnrichedInstrument => {
    if (!inst) {
      return {
        id: '',
        brand: '',
        model: '',
        type: '',
        imagePath: '/images/placeholder.svg',
        displayName: 'Unknown',
        brandLabel: 'Unknown'
      }
    }

    return {
      ...inst,
      imagePath: getInstrumentImage(inst),
      // imageVariants: NOT included here - loaded async when needed
      brandLogo: getBrandLogo(inst.brand),
      // Do not include any price/valor fields for frontend rendering
      // Prices are not rendered in the frontend by design
      displayName: `${inst.model} (${inst.year || '?'})`,
      brandLabel: getBrandById(inst.brand)?.name || inst.brand
    }
  }

  /**
   * Get instruments for a specific brand
   * Returns array of instrument objects with image path included
   */
  const getInstrumentsByBrand = (brandId: string): EnrichedInstrument[] => {
    return instruments.value
      .filter(inst => inst.brand === brandId)
      .map(inst => enrichInstrument(inst))
      .sort((a, b) => a.model.localeCompare(b.model))
  }

  /**
   * Get a specific instrument by ID
   */
  const getInstrumentById = (instrumentId: string): EnrichedInstrument | null => {
    const inst = instruments.value.find(i => i.id === instrumentId)
    return inst ? enrichInstrument(inst) : null
  }

  /**
   * Search instruments by text
   */
  const searchInstruments = (query: string): EnrichedInstrument[] => {
    if (!query || query.trim() === '') return []

    const lower = query.toLowerCase()
    return instruments.value
      .filter(
        inst =>
          inst.model.toLowerCase().includes(lower) ||
          inst.brand.toLowerCase().includes(lower) ||
          inst.description?.toLowerCase().includes(lower)
      )
      .map(inst => enrichInstrument(inst))
  }

  /**
   * Get a summary of the catalog
   */
  const getCatalogStats = computed((): CatalogStats => {
    const brandsCount = brands.value.length
    const instrumentsCount = instruments.value.length
    const instrumentsWithImage = instruments.value.filter(
      i => i.imagen_url || i.image?.url
    ).length

    return {
      totalBrands: brandsCount,
      totalInstruments: instrumentsCount,
      instrumentsWithImage,
      coverage: instrumentsCount > 0
        ? Math.round((instrumentsWithImage / instrumentsCount) * 100)
        : 0
    }
  })

  return {
    // Data refs
    brands,
    instruments,

    // Query methods
    getBrandById,
    getAllBrands,
    getInstrumentsByBrand,
    getInstrumentById,
    getInstrumentImage,
    getInstrumentImageVariants,
    getBrandLogo,
    searchInstruments,

    // Stats
    getCatalogStats
  }
}
