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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useRepairs } from '@/composables/useRepairs'

const route = useRoute()
const {
  currentRepair,
  currentRepairTimeline,
  currentRepairPhotos,
  currentRepairNotes,
  fetchClientRepairDetail,
  downloadClientClosurePdf,
  clearCurrentRepairDetail,
} = useRepairs()
const downloadingPdf = ref(false)
const detail = computed(() => ({
  repair: currentRepair.value,
  timeline: currentRepairTimeline.value || [],
  photos: currentRepairPhotos.value || [],
  notes: currentRepairNotes.value || [],
}))

const formatDate = (value) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' }).format(new Date(value))
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('es-CL', { maximumFractionDigits: 0 }).format(price)
}

async function load() {
  const repairId = route.params.id
  await fetchClientRepairDetail(String(repairId))
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
    const pdfBytes = await downloadClientClosurePdf(String(repairId))
    const blob = new Blob([pdfBytes], { type: 'application/pdf' })
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
  clearCurrentRepairDetail()
})
</script>
