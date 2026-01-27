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

<style lang="scss" scoped>
@import '@/scss/_core.scss';

.admin-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: $spacer-lg;
  background: lighten($vintage-beige, 5%);
  border-radius: $border-radius-lg;
  padding: $spacer-lg $spacer-xl;
  margin: $spacer-lg $spacer-xxl 0;
  border: 1px solid rgba($color-dark, 0.2);
  box-shadow: 0 8px 18px rgba($color-dark, 0.18);
}

.title-block {
  position: relative;
  flex: 1;
}

.title {
  margin: 0;
  color: $color-dark;
  font-size: $h3-size;
}

.subtitle {
  margin: $spacer-xs 0 0;
  color: $text-muted;
  font-size: $text-base;
}

.actions {
  display: flex;
  align-items: center;
  gap: $spacer-md;
}

.global-search {
  margin-top: $spacer-md;
  max-width: 480px;
  position: relative;
}

.search-input {
  width: 100%;
  padding: $spacer-sm $spacer-md;
  border-radius: $border-radius-md;
  border: 1px solid rgba($color-dark, 0.25);
  font-size: $text-base;
  background: $color-white;
}

.search-results {
  position: absolute;
  top: calc(100% + #{$spacer-sm});
  left: 0;
  right: 0;
  background: $color-white;
  border: 1px solid rgba($color-dark, 0.2);
  border-radius: $border-radius-md;
  box-shadow: $shadow-lg;
  z-index: $z-index-dropdown;
  max-height: 320px;
  overflow-y: auto;
}

.search-item {
  width: 100%;
  text-align: left;
  background: transparent;
  border: none;
  padding: $spacer-sm $spacer-md;
  display: flex;
  flex-direction: column;
  gap: $spacer-xs;
  cursor: pointer;
  transition: $transition-fast;
}

.search-item:hover {
  background: rgba($color-primary, 0.12);
}

.search-label {
  font-weight: $fw-semibold;
  color: $color-dark;
}

.search-subtitle {
  font-size: $text-sm;
  color: $text-muted;
}

.search-empty {
  padding: $spacer-sm $spacer-md;
  color: $text-muted;
}

.btn-link {
  color: $color-dark;
  text-decoration: none;
  font-weight: $fw-semibold;
  border-bottom: 1px solid rgba($color-dark, 0.35);
  padding-bottom: 2px;
  transition: $transition-fast;
}

.btn-logout {
  padding: $spacer-sm $spacer-md;
  background: rgba($color-primary, 0.15);
  color: $color-dark;
  border: 2px solid rgba($color-primary, 0.6);
  border-radius: $border-radius-md;
  font-weight: $fw-semibold;
  cursor: pointer;
  transition: $transition-fast;
}

.btn-logout:hover {
  background: rgba($color-primary, 0.3);
  border-color: rgba($color-primary, 0.75);
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
