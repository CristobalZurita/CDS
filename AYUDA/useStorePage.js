/**
 * composables/useStorePage.js
 * Reemplaza el existente.
 * Orquesta catálogo, filtros, búsqueda y paginación.
 * Usa @tanstack/vue-query (ya en package.json).
 */
import { ref, computed, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { fetchProducts, fetchCategories } from '@/services/storeCatalogService.js'
import { useShopCartStore } from '@/stores/shopCart.js'

export function useStorePage() {
  const cart = useShopCartStore()

  // ── Filtros reactivos ─────────────────────────────────────
  const search     = ref('')
  const categoryId = ref(null)
  const sort       = ref('name')
  const page       = ref(1)

  // Reset página al cambiar filtros
  watch([search, categoryId, sort], () => { page.value = 1 })

  // ── Queries ───────────────────────────────────────────────
  const { data: categoriesData } = useQuery({
    queryKey: ['shop-categories'],
    queryFn:  fetchCategories,
    staleTime: 1000 * 60 * 10,
  })

  const productsQueryKey = computed(() => [
    'shop-products',
    { search: search.value, categoryId: categoryId.value, sort: sort.value, page: page.value }
  ])

  const {
    data:       productsData,
    isFetching: isLoading,
    isError,
  } = useQuery({
    queryKey: productsQueryKey,
    queryFn:  () => fetchProducts({
      search:     search.value,
      categoryId: categoryId.value,
      sort:       sort.value,
      page:       page.value,
      limit:      24,
    }),
    keepPreviousData: true,
    staleTime: 1000 * 30,
  })

  // ── Derivados ─────────────────────────────────────────────
  const products   = computed(() => productsData.value?.items   ?? [])
  const totalPages = computed(() => productsData.value?.pages   ?? 1)
  const total      = computed(() => productsData.value?.total   ?? 0)
  const categories = computed(() => categoriesData.value        ?? [])

  const activeCategory = computed(() =>
    categories.value.find(c => c.id === categoryId.value) ?? null
  )

  // ── Acciones ──────────────────────────────────────────────
  function selectCategory(id) {
    categoryId.value = id === categoryId.value ? null : id
  }

  function clearFilters() {
    search.value     = ''
    categoryId.value = null
    sort.value       = 'name'
    page.value       = 1
  }

  function addToCart(product) {
    cart.addItem(product)
  }

  return {
    // estado
    search, categoryId, sort, page,
    // datos
    products, categories, totalPages, total, activeCategory,
    // flags
    isLoading, isError,
    // acciones
    selectCategory, clearFilters, addToCart,
    // cart
    cart,
  }
}
