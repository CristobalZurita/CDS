<template>
  <div class="repair-detail">
    <div class="header">
      <div>
        <h1>{{ detail.repair?.instrument || 'Reparación' }}</h1>
        <p class="muted">Ticket {{ detail.repair?.repair_number || detail.repair?.id }}</p>
      </div>
      <span class="status">{{ detail.repair?.status }}</span>
    </div>

    <section class="card">
      <h3>Resumen</h3>
      <p><strong>Falla:</strong> {{ detail.repair?.problem_reported || '—' }}</p>
      <p><strong>Diagnóstico:</strong> {{ detail.repair?.diagnosis || '—' }}</p>
      <p><strong>Trabajo:</strong> {{ detail.repair?.work_performed || '—' }}</p>
      <p><strong>Costo:</strong> {{ detail.repair?.total_cost ? formatPrice(detail.repair.total_cost) : '—' }}</p>
    </section>

    <section class="card">
      <h3>Timeline</h3>
      <ul>
        <li v-for="item in detail.timeline" :key="item.label">
          {{ item.label }} · {{ formatDate(item.date) }}
        </li>
      </ul>
      <p v-if="!detail.timeline?.length" class="muted">Sin eventos registrados.</p>
    </section>

    <section class="card">
      <h3>Fotos</h3>
      <div class="photos">
        <figure v-for="photo in detail.photos" :key="photo.id">
          <img :src="resolvePhotoUrl(photo)" :alt="photo.caption || 'foto'" />
          <figcaption>{{ photo.caption || 'Foto del proceso' }}</figcaption>
        </figure>
      </div>
      <p v-if="!detail.photos?.length" class="muted">Sin fotos disponibles.</p>
    </section>

    <section class="card">
      <h3>Notas</h3>
      <ul>
        <li v-for="note in detail.notes" :key="note.id">
          {{ note.note }} · {{ formatDate(note.created_at) }}
        </li>
      </ul>
      <p v-if="!detail.notes?.length" class="muted">Sin notas visibles.</p>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/services/api'

const route = useRoute()
const detail = ref({ timeline: [], photos: [], notes: [] })

const formatDate = (value) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' }).format(new Date(value))
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('es-CL', { maximumFractionDigits: 0 }).format(price)
}

const resolvePhotoUrl = (photo) => {
  if (!photo) return ''
  const path = photo.photo_download_url || photo.photo_url || ''
  if (!path) return ''
  if (path.startsWith('http')) return path
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  return `${baseUrl}${path.startsWith('/') ? '' : '/'}${path}`
}

async function load() {
  const repairId = route.params.id
  const res = await api.get(`/client/repairs/${repairId}/details`)
  detail.value = res.data
}

onMounted(load)
</script>

<style scoped>
.repair-detail {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1rem;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.muted {
  color: #6b7280;
}
.status {
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  background: #eef2ff;
}
.card {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fff;
}
.photos {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}
img {
  width: 100%;
  border-radius: 10px;
}
</style>
