<template>
  <main class="repair-detail-page">
    <header class="detail-header">
      <div>
        <h1>{{ detail.repair?.instrument || 'Reparacion' }}</h1>
        <p class="muted">OT {{ detail.repair?.repair_code || detail.repair?.repair_number || detail.repair?.id || '—' }}</p>
      </div>

      <div class="header-actions">
        <router-link to="/repairs" class="btn-secondary">Volver</router-link>
        <button class="btn-primary" data-testid="repair-download" :disabled="downloadingPdf" @click="downloadClosurePdf">
          {{ downloadingPdf ? 'Generando PDF...' : 'Descargar Cierre OT' }}
        </button>
      </div>
    </header>

    <p v-if="loadingError" class="detail-error">{{ loadingError }}</p>

    <section v-if="isLoading" class="detail-card">
      <p>Cargando detalle de reparacion...</p>
    </section>

    <template v-else>
      <section class="detail-card">
        <h2>Resumen</h2>
        <p><strong>Falla:</strong> {{ detail.repair?.problem_reported || '—' }}</p>
        <p><strong>Diagnostico:</strong> {{ detail.repair?.diagnosis || '—' }}</p>
        <p><strong>Trabajo:</strong> {{ detail.repair?.work_performed || '—' }}</p>
        <p><strong>Costo:</strong> {{ detail.repair?.total_cost ? formatPrice(detail.repair.total_cost) : '—' }}</p>
      </section>

      <section class="detail-card">
        <h2>Timeline</h2>
        <ul v-if="detail.timeline.length > 0" class="timeline-list">
          <li v-for="item in detail.timeline" :key="`${item.label}-${item.date}`">
            <strong>{{ item.label || 'Evento' }}</strong>
            <span>{{ formatDate(item.date) }}</span>
          </li>
        </ul>
        <p v-else class="muted">Sin eventos registrados.</p>
      </section>

      <section class="detail-card">
        <h2>Fotos</h2>
        <div v-if="detail.photos.length > 0" class="photos-grid">
          <figure v-for="photo in detail.photos" :key="photo.id" class="photo-item">
            <img
              :src="photo.resolved_photo_url"
              :alt="photo.caption || 'Foto de reparacion'"
              loading="lazy"
              width="400"
              height="300"
            />
            <figcaption>{{ photo.caption || 'Foto del proceso' }}</figcaption>
          </figure>
        </div>
        <p v-else class="muted">Sin fotos disponibles.</p>
      </section>

      <section class="detail-card">
        <h2>Notas</h2>
        <ul v-if="detail.notes.length > 0" class="notes-list">
          <li v-for="note in detail.notes" :key="note.id">
            <p>{{ note.note || 'Sin contenido' }}</p>
            <small>{{ formatDate(note.created_at) }}</small>
          </li>
        </ul>
        <p v-else class="muted">Sin notas visibles.</p>
      </section>
    </template>
  </main>
</template>

<script setup>
import { useRepairDetailPage } from '@/composables/useRepairDetailPage'

const {
  detail,
  isLoading,
  loadingError,
  downloadingPdf,
  formatDate,
  formatPrice,
  downloadClosurePdf
} = useRepairDetailPage()
</script>

<style scoped src="./commonClientPage.css"></style>
