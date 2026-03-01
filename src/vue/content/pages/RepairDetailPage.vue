<template>
  <div class="repair-detail">
    <div class="header">
      <div>
        <h1>{{ detail.repair?.instrument || 'Reparación' }}</h1>
        <p class="muted">OT {{ detail.repair?.repair_code || detail.repair?.repair_number || detail.repair?.id }}</p>
      </div>
      <div class="header-actions">
        <span class="status">{{ detail.repair?.status }}</span>
        <button class="btn-download" data-testid="repair-download" :disabled="downloadingPdf" @click="downloadClosurePdf">
          {{ downloadingPdf ? 'Generando PDF...' : 'Descargar Cierre OT' }}
        </button>
      </div>
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
          <img 
            :src="photo.resolved_photo_url" 
            :alt="photo.caption || 'foto'"
            loading="lazy"
            width="400"
            height="300"
          />
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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/services/api'
import { hydrateRepairPhotos, revokeHydratedRepairPhotos } from '@/services/secureMedia'

const route = useRoute()
const detail = ref({ timeline: [], photos: [], notes: [] })
const downloadingPdf = ref(false)

const formatDate = (value) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' }).format(new Date(value))
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('es-CL', { maximumFractionDigits: 0 }).format(price)
}

async function load() {
  const repairId = route.params.id
  const res = await api.get(`/client/repairs/${repairId}/details`)
  const resolvedPhotos = await hydrateRepairPhotos(res.data?.photos || [])
  detail.value = {
    ...res.data,
    photos: resolvedPhotos,
  }
}

const sanitizeFilePart = (value) => {
  const text = String(value || '').trim()
  if (!text) return 'OT'
  return text.replace(/[^a-zA-Z0-9._-]+/g, '_')
}

async function downloadClosurePdf() {
  downloadingPdf.value = true
  try {
    const repairId = route.params.id
    const response = await api.get(`/client/repairs/${repairId}/closure-pdf`, {
      responseType: 'blob'
    })
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const blobUrl = window.URL.createObjectURL(blob)
    const preferredCode = detail.value?.repair?.repair_code || detail.value?.repair?.repair_number || detail.value?.repair?.id || `OT_${repairId}`
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = `CIERRE_CLIENTE_${sanitizeFilePart(preferredCode)}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(blobUrl)
  } catch (error) {
    window.alert(error?.response?.data?.detail || 'No se pudo descargar el PDF de cierre.')
  } finally {
    downloadingPdf.value = false
  }
}

onMounted(load)
onBeforeUnmount(() => {
  revokeHydratedRepairPhotos(detail.value?.photos || [])
})
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

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
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.muted {
  color: $color-gray-500-legacy;
}
.status {
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  background: $color-indigo-50-legacy;
}
.btn-download {
  border: 1px solid $color-gray-200-legacy;
  background: $color-white;
  border-radius: 10px;
  padding: 0.4rem 0.65rem;
  font-size: 0.82rem;
}
.btn-download:disabled {
  opacity: 0.7;
}
.card {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid $color-gray-200-legacy;
  border-radius: 12px;
  background: $color-white;
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
