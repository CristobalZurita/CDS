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
    router.push('/admin/archive')
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

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

.admin-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  background: lighten($vintage-beige, 5%);
  border-radius: 12px;
  padding: 1.6rem 2rem;
  margin: 1.75rem 2.5rem 0;
  border: 1px solid rgba(62, 60, 56, 0.2);
  box-shadow: 0 8px 18px rgba(62, 60, 56, 0.18);
}
.title-block {
  position: relative;
  flex: 1;
}

.title {
  margin: 0;
  color: $brand-text;
  font-size: 1.8rem;
}

.subtitle {
  margin: 0.35rem 0 0;
  color: $text-muted;
  font-size: 1rem;
}

.actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.global-search {
  margin-top: 0.9rem;
  max-width: 480px;
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.7rem 0.9rem;
  border-radius: 10px;
  border: 1px solid rgba(62, 60, 56, 0.25);
  font-size: 0.98rem;
  background: #fff;
}

.search-results {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid rgba(62, 60, 56, 0.2);
  border-radius: 10px;
  box-shadow: 0 10px 24px rgba(62, 60, 56, 0.2);
  z-index: 20;
  max-height: 320px;
  overflow-y: auto;
}

.search-item {
  width: 100%;
  text-align: left;
  background: transparent;
  border: none;
  padding: 0.75rem 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  cursor: pointer;
}

.search-item:hover {
  background: rgba(236, 107, 0, 0.12);
}

.search-label {
  font-weight: 600;
  color: $brand-text;
}

.search-subtitle {
  font-size: 0.85rem;
  color: $text-muted;
}

.search-empty {
  padding: 0.85rem 0.9rem;
  color: $text-muted;
}

.btn-link {
  color: $brand-text;
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px solid rgba(62, 60, 56, 0.35);
  padding-bottom: 2px;
}

.btn-logout {
  padding: 0.65rem 1.2rem;
  background: rgba(236, 107, 0, 0.15);
  color: $brand-text;
  border: 2px solid rgba(236, 107, 0, 0.6);
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: rgba(236, 107, 0, 0.3);
  border-color: rgba(236, 107, 0, 0.75);
}

@include media-breakpoint-down(md) {
  .admin-topbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>
