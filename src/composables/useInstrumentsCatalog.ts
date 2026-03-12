import { ref, computed } from 'vue'
import brandsData from '@/assets/data/brands.json'
import instrumentsData from '@/data/instruments.json'
import { toCloudinaryUrl } from '../CDS_VUE3_ZERO/src/utils/cloudinary.js'
import type { ComputedRef, Ref } from 'vue'

interface Brand {
  id: string
  name: string
  tier?: string
  founded?: number | null
  country?: string | null
  description?: string
  [key: string]: unknown
}

interface SyncedInstrument {
  id: string
  marca: string
  modelo: string
  foto_principal: string
  fotos_adicionales: string[]
  tipos?: string[]
  agregado_en?: string
  marca_logo_disponible?: boolean
  marca_habilitada?: boolean
  marca_logo_url?: string | null
  [key: string]: unknown
}

interface SyncedInstrumentsPayload {
  instruments?: SyncedInstrument[]
  marcas_habilitadas?: string[]
}

interface Instrument extends SyncedInstrument {
  brand: string
  model: string
  type: string
  year?: number | null
  description?: string
  imagen_url?: string
  photo_key?: string
  display_model?: string
}

interface EnrichedInstrument extends Instrument {
  imagePath: string
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
  brands: Ref<Brand[]>
  instruments: Ref<Instrument[]>
  getBrandById: (brandId: string) => Brand | undefined
  getAllBrands: (sorted?: boolean) => Brand[]
  getInstrumentsByBrand: (brandId: string) => EnrichedInstrument[]
  getInstrumentById: (instrumentId: string) => EnrichedInstrument | null
  getInstrumentImage: (instrument: Instrument) => string
  getInstrumentImageVariants: (instrument: Instrument) => Promise<string[]>
  getBrandLogo: (brandId: string) => string
  searchInstruments: (query: string) => EnrichedInstrument[]
  getCatalogStats: ComputedRef<CatalogStats>
}

const BRAND_ID_ALIASES: Record<string, string> = {
  ACCESS: 'access',
  AKAI: 'akai',
  ALESIS: 'alesis',
  ARTURIA: 'arturia',
  ASM: 'asm',
  BEHERINGER: 'behringer',
  CASIO: 'casio',
  KAWAI: 'kawai',
  KORG: 'korg',
  NOVATION: 'novation',
  ROLAND: 'roland',
  STUDIOLOGIC: 'studiologic',
  YAMAHA: 'yamaha',
}

const BRAND_CANONICAL_ALIASES: Record<string, string> = {
  ACCES: 'ACCESS',
}

const toCanonicalBrand = (marca: string): string =>
  BRAND_CANONICAL_ALIASES[marca] || marca

const toBrandId = (marca: string): string => {
  const canonical = toCanonicalBrand((marca || '').toUpperCase())
  return BRAND_ID_ALIASES[canonical] || canonical.toLowerCase().replace(/\s+/g, '-')
}

const normalizeModel = (modelo: string): string => String(modelo || '').replace(/_/g, ' ')

const buildInstrumentPath = (photoName: string): string =>
  toCloudinaryUrl(`/images/instrumentos/${photoName}.webp`)

export function useInstrumentsCatalog(): UseInstrumentsCatalogComposable {
  const syncedPayload = instrumentsData as SyncedInstrumentsPayload
  const allRawInstruments: SyncedInstrument[] = Array.isArray(syncedPayload?.instruments)
    ? (syncedPayload.instruments as SyncedInstrument[])
    : []

  const allNormalizedInstruments: Instrument[] = allRawInstruments.map((inst) => {
    const brandId = toBrandId(inst.marca)
    const fotoPrincipal = inst.foto_principal
    const fotosAdicionales = Array.isArray(inst.fotos_adicionales)
      ? inst.fotos_adicionales
      : []

    return {
      ...inst,
      id: inst.id,
      brand: brandId,
      model: normalizeModel(inst.modelo),
      type: 'Keyboard / Synthesizer',
      year: null,
      description: `Instrumento ${normalizeModel(inst.modelo)}`.trim(),
      imagen_url: buildInstrumentPath(fotoPrincipal),
      photo_key: fotoPrincipal,
      foto_principal: fotoPrincipal,
      fotos_adicionales: fotosAdicionales,
      marca: toCanonicalBrand(inst.marca),
      marca_logo_disponible: Boolean(inst.marca_logo_disponible),
      marca_habilitada: Boolean(inst.marca_habilitada),
      marca_logo_url: inst.marca_logo_url || null,
      display_model: normalizeModel(inst.modelo),
    }
  })

  const enabledBrandAllowList = new Set(
    Array.isArray(syncedPayload?.marcas_habilitadas)
      ? syncedPayload.marcas_habilitadas.map((marca) => toBrandId(String(marca)))
      : []
  )
  const hasEnabledBrandAllowList = enabledBrandAllowList.size > 0

  const enabledInstruments = allNormalizedInstruments.filter((inst) => {
    const hasBrandLogo = Boolean(inst.marca_logo_disponible && inst.marca_logo_url)
    const isBrandEnabled = Boolean(inst.marca_habilitada)
    const isAllowedBySync = !hasEnabledBrandAllowList || enabledBrandAllowList.has(inst.brand)
    return hasBrandLogo && isBrandEnabled && isAllowedBySync
  })

  const brandLogoById: Record<string, string> = {}
  enabledInstruments.forEach((inst) => {
    if (inst.brand && inst.marca_logo_url && !brandLogoById[inst.brand]) {
      brandLogoById[inst.brand] = String(inst.marca_logo_url)
    }
  })

  const enabledBrandIds = new Set(enabledInstruments.map(inst => inst.brand))
  const knownBrands = Array.isArray(brandsData?.brands) ? (brandsData.brands as Brand[]) : []
  const filteredKnownBrands = knownBrands.filter(brand => enabledBrandIds.has(brand.id))
  const missingBrands: Brand[] = Array.from(enabledBrandIds)
    .filter(brandId => !filteredKnownBrands.some(brand => brand.id === brandId))
    .map((brandId) => ({
      id: brandId,
      name: brandId.toUpperCase(),
      tier: 'standard',
      founded: null,
      country: null,
      description: 'Marca detectada por fotos sincronizadas',
    }))

  const brands = ref<Brand[]>([...filteredKnownBrands, ...missingBrands])
  const instruments = ref<Instrument[]>(enabledInstruments)

  const getBrandById = (brandId: string): Brand | undefined =>
    brands.value.find(brand => brand.id === brandId)

  const getAllBrands = (sorted = true): Brand[] => {
    const list = [...brands.value]
    if (sorted) {
      return list.sort((a, b) => a.name.localeCompare(b.name))
    }
    return list
  }

  const getInstrumentImage = (instrument: Instrument): string => {
    if (instrument?.foto_principal) {
      return buildInstrumentPath(instrument.foto_principal)
    }
    if (instrument?.photo_key) {
      return buildInstrumentPath(instrument.photo_key)
    }
    if (instrument?.imagen_url) {
      return instrument.imagen_url
    }
    return toCloudinaryUrl('/images/placeholder.svg')
  }

  const getInstrumentImageVariants = async (instrument: Instrument): Promise<string[]> => {
    if (!instrument) return []

    const photos: string[] = []
    if (instrument.foto_principal) {
      photos.push(instrument.foto_principal)
    } else if (instrument.photo_key) {
      photos.push(instrument.photo_key)
    }

    if (Array.isArray(instrument.fotos_adicionales)) {
      photos.push(...instrument.fotos_adicionales)
    }

    return [...new Set(photos)].map(buildInstrumentPath)
  }

  const getBrandLogo = (brandId: string): string => {
    if (!brandId) return ''
    if (brandLogoById[brandId]) return toCloudinaryUrl(brandLogoById[brandId])

    const normalized = String(brandId).toUpperCase().replace(/-/g, '_')
    const brandLogoFixes: Record<string, string> = {
      BEHRINGER: 'BEHERINGER',
    }
    const logoKey = brandLogoFixes[normalized] || normalized
    return toCloudinaryUrl(`/images/instrumentos/LOGOS/LOGO_${logoKey}.webp`)
  }

  const enrichInstrument = (inst: Instrument): EnrichedInstrument => {
    return {
      ...inst,
      imagePath: getInstrumentImage(inst),
      brandLogo: getBrandLogo(inst.brand),
      displayName: inst.display_model || inst.model,
      brandLabel: getBrandById(inst.brand)?.name || inst.marca || inst.brand,
    }
  }

  const getInstrumentsByBrand = (brandId: string): EnrichedInstrument[] =>
    instruments.value
      .filter(inst => inst.brand === brandId)
      .map(inst => enrichInstrument(inst))
      .sort((a, b) => (a.model || '').localeCompare(b.model || ''))

  const getInstrumentById = (instrumentId: string): EnrichedInstrument | null => {
    const inst = instruments.value.find(i => i.id === instrumentId)
    return inst ? enrichInstrument(inst) : null
  }

  const searchInstruments = (query: string): EnrichedInstrument[] => {
    if (!query || query.trim() === '') return []
    const lower = query.toLowerCase()
    return instruments.value
      .filter(inst =>
        (inst.model || '').toLowerCase().includes(lower) ||
        (inst.marca || '').toLowerCase().includes(lower) ||
        (inst.description || '').toLowerCase().includes(lower)
      )
      .map(inst => enrichInstrument(inst))
  }

  const getCatalogStats = computed((): CatalogStats => {
    const totalBrands = brands.value.length
    const totalInstruments = instruments.value.length
    const instrumentsWithImage = instruments.value.filter(i => Boolean(i.foto_principal)).length
    return {
      totalBrands,
      totalInstruments,
      instrumentsWithImage,
      coverage: totalInstruments > 0
        ? Math.round((instrumentsWithImage / totalInstruments) * 100)
        : 0,
    }
  })

  return {
    brands,
    instruments,
    getBrandById,
    getAllBrands,
    getInstrumentsByBrand,
    getInstrumentById,
    getInstrumentImage,
    getInstrumentImageVariants,
    getBrandLogo,
    searchInstruments,
    getCatalogStats,
  }
}
