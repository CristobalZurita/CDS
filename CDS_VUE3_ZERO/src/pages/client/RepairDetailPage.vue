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
import { useRepairDetailPage } from '@new/composables/useRepairDetailPage'

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

<style scoped>
.repair-detail-page {
  padding: 1rem;
  display: grid;
  gap: 1rem;
}

.detail-header,
.detail-card {
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.9rem;
  background: var(--cds-white);
}

.detail-header {
  padding: 1rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
}

.detail-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
}

.muted {
  margin: 0.3rem 0 0;
  color: var(--cds-text-muted);
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.btn-primary,
.btn-secondary {
  min-height: 44px;
  padding: 0.65rem 0.9rem;
  border-radius: 0.55rem;
  font-size: var(--cds-text-base);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  border: 1px solid var(--cds-primary);
  background: var(--cds-primary);
  color: var(--cds-white);
}

.btn-secondary {
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  background: var(--cds-white);
  color: var(--cds-text-normal);
}

.detail-error {
  margin: 0;
  border: 1px solid #f4c7c3;
  background: #fef3f2;
  color: #b42318;
  border-radius: 0.6rem;
  padding: 0.75rem;
}

.detail-card {
  padding: 0.95rem;
  display: grid;
  gap: 0.6rem;
}

.detail-card h2 {
  margin: 0;
  font-size: var(--cds-text-xl);
}

.detail-card p {
  margin: 0;
}

.timeline-list,
.notes-list {
  margin: 0;
  padding-left: 1rem;
  display: grid;
  gap: 0.45rem;
}

.timeline-list li,
.notes-list li {
  display: grid;
  gap: 0.2rem;
}

.photos-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.photo-item {
  margin: 0;
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  border-radius: 0.7rem;
  overflow: hidden;
  background: var(--cds-white);
}

.photo-item img {
  width: 100%;
  height: 220px;
  object-fit: cover;
  display: block;
}

.photo-item figcaption {
  padding: 0.55rem 0.65rem;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.notes-list small {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

@media (min-width: 860px) {
  .photos-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
