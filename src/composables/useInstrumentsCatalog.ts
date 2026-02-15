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
  searchInstruments: (query: string) => EnrichedInstrument[]

  // Stats
  getCatalogStats: ComputedRef<CatalogStats>
}

/**
 * useInstrumentsCatalog - Central data catalog for brands and instruments
 *
 * This composable provides:
 * - Unified access to brands and instruments
 * - Brand → Instruments mapping
 * - Image path generation based on instrument ID
 * - No database needed; all data derived from JSON
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
   * Generate image path for an instrument
   * Convention: /images/instruments/{instrument.id}.webp (now prioritizing WebP format)
   * Falls back to placeholder if not found
   */
  const getInstrumentImage = (instrument: Instrument): string => {
    // Priority 1: Use existing imagen_url if valid
    if (instrument?.imagen_url) {
      return instrument.imagen_url
    }

    // Priority 2: Generate from convention (use Spanish 'instrumentos' directory)
    if (instrument?.id) {
      // Try common filename variations so we match existing images in /public/images/instrumentos
      const id = instrument.id
      const model = (instrument.model || '').replace(/\s+/g, '_')
      const brand = (instrument.brand || '').toUpperCase()
      const brandModel = `${brand}_${model.toUpperCase()}`

      // Prefer WebP (modern, efficient format) and common extensions
      const candidates = [
        // Brand logo fallbacks (prioritize WebP)
        `/images/instrumentos/LOGO_${brand}.webp`,
        `/images/instrumentos/LOGO_${brand}.webp`,
        `/images/instrumentos/LOGO_${brand}.webp`,

        // BRAND_MODEL uppercase with common extensions (WebP first)
        `/images/instrumentos/${brandModel}.webp`,
        `/images/instrumentos/${brandModel}.webp`,
        `/images/instrumentos/${brandModel}.webp`,
        `/images/instrumentos/${brandModel}.avif`,

        // ID derived variants (uppercase underscore), try WebP first
        `/images/instrumentos/${id.replace(/-/g, '_').toUpperCase()}.webp`,
        `/images/instrumentos/${id.replace(/-/g, '_').toUpperCase()}.jpg`,
        `/images/instrumentos/${id.replace(/-/g, '_').toUpperCase()}.png`,

        // ID uppercase (WebP first)
        `/images/instrumentos/${id.toUpperCase()}.webp`,
        `/images/instrumentos/${id.toUpperCase()}.webp`,
        `/images/instrumentos/${id.toUpperCase()}.webp`,

        // Original id (lowercase) fallbacks (WebP first)
        `/images/instrumentos/${id}.webp`,
        `/images/instrumentos/${id}.webp`,
        `/images/instrumentos/${id}.webp`,

        // Model-based fallbacks (WebP first)
        `/images/instrumentos/${model}.webp`,
        `/images/instrumentos/${model}.webp`,
        `/images/instrumentos/${model}.webp`
      ]

      // Return the most likely candidate (first in list). If a given file doesn't exist,
      // the browser will 404 and the UI will show the placeholder. This ordering improves
      // hit-rate for WebP images that are now the primary format in the repo.
      return candidates[0]
    }

    // Priority 3: Placeholder
    return '/images/placeholder.svg'
  }

  /**
   * Enrich instrument object with computed fields
   * (adds image path, formatted price, etc.)
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
    searchInstruments,

    // Stats
    getCatalogStats
  }
}
