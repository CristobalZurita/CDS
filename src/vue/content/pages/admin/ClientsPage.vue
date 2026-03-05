
<template>
  <AdminLayout title="Clientes" subtitle="Gestión de clientes y perfil" :context="contextHeader">
    <section class="clients-page">
      <header class="clients-page__header">
        <h1 class="clients-page__title">Clientes</h1>

        <div class="clients-page__actions">
          <button
            type="button"
            class="clients-page__button clients-page__button--primary"
            data-testid="clients-intake-toggle"
            @click="showIntake = !showIntake"
          >
            {{ showIntake ? 'Cerrar ingreso' : 'Ingreso completo' }}
          </button>
          <button
            type="button"
            class="clients-page__button clients-page__button--secondary"
            data-testid="clients-refresh"
            @click="load"
          >
            Actualizar
          </button>
        </div>
      </header>

      <section v-if="showIntake" class="clients-page__panel" data-testid="clients-intake">
        <UnifiedIntakeForm @completed="onIntakeCompleted" />
      </section>

      <section class="clients-page__panel">
        <div class="clients-page__toolbar">
          <input
            v-model="searchQuery"
            type="search"
            class="clients-page__input"
            data-testid="clients-search"
            placeholder="Buscar por nombre, email, código o teléfono..."
          />
        </div>

        <div class="clients-page__grid">
          <ClientList :clients="filteredClients" @select="onSelect" />
          <ClientDetail :client="selected || {}" />
        </div>
      </section>
    </section>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/services/api'
import ClientList from '@/vue/components/admin/ClientList.vue'
import ClientDetail from '@/vue/components/admin/ClientDetail.vue'
import UnifiedIntakeForm from '@/vue/components/admin/UnifiedIntakeForm.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const clients = ref([])
const selected = ref(null)
const showIntake = ref(true)
const searchQuery = ref('')
const route = useRoute()
const contextHeader = computed(() => {
	if (!selected.value) return null
	return {
		clientName: selected.value.name,
		clientCode: selected.value.client_code,
		instrument: '—'
	}
})

const filteredClients = computed(() => {
	const q = searchQuery.value.trim().toLowerCase()
	if (!q) return clients.value
	return clients.value.filter((client) => {
		const haystack = [
			client.name,
			client.email,
			client.phone,
			client.client_code
		].filter(Boolean).join(' ').toLowerCase()
		return haystack.includes(q)
	})
})

async function load() {
	try {
		const res = await api.get('/clients')
		clients.value = res.data
		if (route.query.client_id) {
			const found = clients.value.find(c => String(c.id) === String(route.query.client_id))
			selected.value = found || clients.value[0] || null
		} else {
			selected.value = clients.value[0] || null
		}
	} catch {
		clients.value = []
	}
}

function onSelect(client) {
	selected.value = client
}

function onIntakeCompleted(payload) {
	showIntake.value = false
	load()
	if (payload?.client_id) {
		const found = clients.value.find(c => String(c.id) === String(payload.client_id))
		if (found) selected.value = found
	}
}

onMounted(load)
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.clients-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.clients-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacer-md);
  flex-wrap: wrap;
}

.clients-page__title {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--text-xl);
  font-weight: 700;
}

.clients-page__actions {
  display: flex;
  gap: var(--spacer-sm);
  flex-wrap: wrap;
}

.clients-page__panel {
  padding: var(--spacer-md);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.clients-page__toolbar {
  margin-bottom: var(--spacer-md);
}

.clients-page__input {
  width: 100%;
  min-height: 44px;
  padding: 0.75rem 0.875rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
  background: var(--color-white);
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.clients-page__grid {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) minmax(0, 1.35fr);
  gap: var(--spacer-md);
  align-items: start;
}

.clients-page__button {
  min-height: 40px;
  padding: 0.65rem 0.95rem;
  border: 0;
  border-radius: var(--radius-sm);
  color: var(--color-white);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
}

.clients-page__button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.clients-page__button--primary {
  background: var(--color-primary);
}

.clients-page__button--secondary {
  background: var(--color-dark);
}

@include media-breakpoint-down(md) {
  .clients-page__header,
  .clients-page__actions,
  .clients-page__grid {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: stretch;
  }

  .clients-page__button {
    width: 100%;
  }
}
</style>
