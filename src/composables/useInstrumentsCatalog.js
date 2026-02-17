import { ref, computed } from 'vue'
import brandsData from '@/assets/data/brands.json'
import instrumentsData from '@/data/instruments.json'

const BRAND_ID_ALIASES = {
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

const BRAND_CANONICAL_ALIASES = {
  ACCES: 'ACCESS',
}

const FALLBACK_BRAND_NAMES = {
  asm: 'ASM',
  studiologic: 'Studiologic',
}

const toCanonicalBrand = (marca) => BRAND_CANONICAL_ALIASES[marca] || marca

const toBrandId = (marca) => {
  const canonical = toCanonicalBrand((marca || '').toUpperCase())
  return BRAND_ID_ALIASES[canonical] || canonical.toLowerCase().replace(/\s+/g, '-')
}

const normalizeModel = (modelo) => {
  if (!modelo) return ''
  return String(modelo).replace(/_/g, ' ')
}

const buildInstrumentPath = (photoName) => `/images/instrumentos/${photoName}.webp`

export function useInstrumentsCatalog() {
  const allRawInstruments = Array.isArray(instrumentsData?.instruments)
    ? instrumentsData.instruments
    : []

  const allNormalizedInstruments = allRawInstruments.map((inst) => {
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

  const enabledInstruments = allNormalizedInstruments.filter(
    inst => inst.marca_habilitada && inst.marca_logo_disponible
  )

  const brandLogoById = {}
  enabledInstruments.forEach((inst) => {
    if (inst.brand && inst.marca_logo_url && !brandLogoById[inst.brand]) {
      brandLogoById[inst.brand] = inst.marca_logo_url
    }
  })

  const enabledBrandIds = new Set(enabledInstruments.map(inst => inst.brand))

  const knownBrands = Array.isArray(brandsData?.brands) ? brandsData.brands : []
  const filteredKnownBrands = knownBrands.filter(brand => enabledBrandIds.has(brand.id))

  const missingBrands = Array.from(enabledBrandIds)
    .filter(brandId => !filteredKnownBrands.some(brand => brand.id === brandId))
    .map(brandId => ({
      id: brandId,
      name: FALLBACK_BRAND_NAMES[brandId] || brandId.toUpperCase(),
      tier: 'standard',
      founded: null,
      country: null,
      description: 'Marca detectada por fotos sincronizadas',
    }))

  const brands = ref([...filteredKnownBrands, ...missingBrands])
  const instruments = ref(enabledInstruments)

  const getBrandById = (brandId) => {
    return brands.value.find((brand) => brand.id === brandId)
  }

  const getAllBrands = (sorted = true) => {
    const list = [...brands.value]
    if (sorted) {
      return list.sort((a, b) => a.name.localeCompare(b.name))
    }
    return list
  }

  const getInstrumentImage = (instrument) => {
    if (instrument?.foto_principal) {
      return buildInstrumentPath(instrument.foto_principal)
    }
    if (instrument?.photo_key) {
      return buildInstrumentPath(instrument.photo_key)
    }
    if (instrument?.imagen_url) {
      return instrument.imagen_url
    }
    return '/images/placeholder.svg'
  }

  const getInstrumentImageVariants = async (instrument) => {
    if (!instrument) return []

    const photos = []
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

  const getBrandLogo = (brandId) => {
    if (!brandId) return ''
    if (brandLogoById[brandId]) return brandLogoById[brandId]
    const normalized = String(brandId).toUpperCase().replace(/-/g, '_')
    const brandLogoFixes = {
      BEHRINGER: 'BEHERINGER',
    }
    const logoKey = brandLogoFixes[normalized] || normalized
    return `/images/instrumentos/LOGOS/LOGO_${logoKey}.webp`
  }

  const enrichInstrument = (inst) => {
    if (!inst) return null

    return {
      ...inst,
      imagePath: getInstrumentImage(inst),
      brandLogo: getBrandLogo(inst.brand),
      displayName: inst.display_model || inst.model,
      brandLabel: getBrandById(inst.brand)?.name || inst.marca || inst.brand,
    }
  }

  const getInstrumentsByBrand = (brandId) => {
    return instruments.value
      .filter(inst => inst.brand === brandId)
      .map(inst => enrichInstrument(inst))
      .sort((a, b) => (a.model || '').localeCompare(b.model || ''))
  }

  const getInstrumentById = (instrumentId) => {
    const inst = instruments.value.find(i => i.id === instrumentId)
    return inst ? enrichInstrument(inst) : null
  }

  const searchInstruments = (query) => {
    if (!query || query.trim() === '') return []
    const lower = query.toLowerCase()
    return instruments.value
      .filter((inst) =>
        (inst.model || '').toLowerCase().includes(lower) ||
        (inst.marca || '').toLowerCase().includes(lower) ||
        (inst.description || '').toLowerCase().includes(lower)
      )
      .map(inst => enrichInstrument(inst))
  }

  const getCatalogStats = computed(() => {
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
