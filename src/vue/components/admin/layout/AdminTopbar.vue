<template>
  <header class="admin-topbar">
    <div class="title-block">
      <h1 class="title">{{ title || 'Panel Administrativo' }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
      <div class="global-search">
        <input
          v-model="searchQuery"
          type="search"
          class="search-input"
          placeholder="Buscar cliente, OT, instrumento..."
          @input="onSearchInput"
        />
        <div v-if="showResults" class="search-results">
          <div v-if="results.length === 0" class="search-empty">Sin resultados</div>
          <button
            v-for="item in results"
            :key="`${item.type}-${item.id}`"
            class="search-item"
            @click="goToResult(item)"
          >
            <span class="search-label">{{ item.label }}</span>
            <span class="search-subtitle">{{ item.subtitle || item.type }}</span>
          </button>
        </div>
      </div>
    </div>
    <div class="actions">
      <router-link to="/dashboard" class="btn-link">Ver panel cliente</router-link>
      <button class="btn-logout" type="button" @click="handleLogout">
        Cerrar sesión
      </button>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' }
})

const authStore = useAuthStore()
const router = useRouter()
const searchQuery = ref('')
const results = ref([])
const showResults = ref(false)
let debounceTimer = null

const onSearchInput = () => {
  clearTimeout(debounceTimer)
  const q = searchQuery.value.trim()
  if (q.length < 2) {
    results.value = []
    showResults.value = false
    return
  }
  debounceTimer = setTimeout(async () => {
    try {
      const res = await api.get(`/search/?query=${encodeURIComponent(q)}`)
      results.value = res.data || res || []
      showResults.value = true
    } catch (e) {
      results.value = []
      showResults.value = true
    }
  }, 250)
}

const goToResult = (item) => {
  showResults.value = false
  searchQuery.value = ''
  if (item.type === 'repair') {
    router.push(`/admin/repairs/${item.repair_id || item.id}`)
    return
  }
  if (item.type === 'quote') {
    router.push(`/admin/quotes?quote_id=${item.quote_id || item.id}`)
    return
  }
  if (item.type === 'inventory') {
    router.push(`/admin/inventory?edit=${item.product_id || item.id}`)
    return
  }
  if (item.type === 'client' || item.type === 'device') {
    router.push(`/admin/clients?client_id=${item.client_id || item.id}`)
    return
  }
  if (item.type === 'ticket') {
    router.push('/admin/tickets')
    return
  }
  if (item.type === 'manual') {
    router.push('/admin/manuals')
    return
  }
  if (item.type === 'purchase_request') {
    router.push('/admin/purchase-requests')
    return
  }
  router.push('/admin')
}

const handleLogout = () => {
  authStore.logout()
}
</script>
