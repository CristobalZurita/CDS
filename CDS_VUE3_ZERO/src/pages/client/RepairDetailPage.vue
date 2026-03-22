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
      <!-- Barra de progreso -->
      <section class="detail-card progress-card">
        <div class="progress-header">
          <span class="progress-status">{{ detail.repair?.status_normalized || detail.repair?.status || '—' }}</span>
          <span v-if="detail.clockify_hours > 0" class="progress-hours">
            <i class="fa-regular fa-clock"></i>
            {{ detail.clockify_hours }} hrs trabajadas
          </span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: (detail.repair?.progress_pct || 0) + '%' }"></div>
        </div>
        <div class="progress-steps">
          <span v-for="step in progressSteps" :key="step.code"
            class="progress-step"
            :class="{ 'progress-step--done': (detail.repair?.progress_pct || 0) >= step.pct }"
          >{{ step.label }}</span>
        </div>
      </section>

      <section class="detail-card">
        <h2>Resumen</h2>
        <p><strong>Falla reportada:</strong> {{ detail.repair?.problem_reported || '—' }}</p>
        <p v-if="detail.repair?.diagnosis"><strong>Diagnóstico:</strong> {{ detail.repair.diagnosis }}</p>
        <p v-if="detail.repair?.work_performed"><strong>Trabajo realizado:</strong> {{ detail.repair.work_performed }}</p>
        <p><strong>Costo:</strong> {{ detail.repair?.total_cost ? formatPrice(detail.repair.total_cost) : 'Por definir' }}</p>
      </section>

      <section class="detail-card">
        <h2>Proceso</h2>
        <ul v-if="detail.timeline.length > 0" class="timeline-list">
          <li v-for="item in detail.timeline" :key="`${item.label}-${item.date}`">
            <i class="fa-solid fa-circle-check timeline-icon"></i>
            <div>
              <strong>{{ item.label || 'Evento' }}</strong>
              <span class="timeline-date">{{ formatDate(item.date) }}</span>
            </div>
          </li>
        </ul>
        <p v-else class="muted">Aún sin eventos registrados.</p>
      </section>

      <section v-if="detail.photos.length > 0" class="detail-card">
        <h2>Fotos del proceso</h2>
        <div class="photos-grid">
          <figure v-for="photo in detail.photos" :key="photo.id" class="photo-item">
            <img
              :src="photo.resolved_photo_url"
              :alt="photo.caption || 'Foto del proceso'"
              loading="lazy"
            />
            <figcaption>{{ photo.caption || '' }}</figcaption>
          </figure>
        </div>
      </section>

      <section v-if="detail.notes.length > 0" class="detail-card">
        <h2>Comentarios</h2>
        <ul class="notes-list">
          <li v-for="note in detail.notes" :key="note.id">
            <p>{{ note.note }}</p>
            <small class="muted">{{ formatDate(note.created_at) }}</small>
          </li>
        </ul>
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

const progressSteps = [
  { code: 'ingreso',      label: 'Ingreso',      pct: 10 },
  { code: 'diagnostico',  label: 'Diagnóstico',  pct: 20 },
  { code: 'aprobado',     label: 'Aprobado',     pct: 40 },
  { code: 'en_trabajo',   label: 'En trabajo',   pct: 60 },
  { code: 'listo',        label: 'Listo',        pct: 80 },
  { code: 'entregado',    label: 'Entregado',    pct: 100 },
]
</script>

<style scoped src="./commonClientPage.css"></style>

<style scoped>
/* ── Barra de progreso ── */
.progress-card {
  display: grid;
  gap: 0.6rem;
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.progress-status {
  font-weight: 600;
  font-size: var(--cds-text-sm);
  text-transform: capitalize;
  color: var(--cds-primary);
}

.progress-hours {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted, #888);
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.progress-track {
  height: 8px;
  border-radius: 999px;
  background: rgba(0,0,0,0.1);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  background: var(--cds-primary);
  transition: width 0.5s ease;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  gap: 0.25rem;
}

.progress-step {
  font-size: 0.7rem;
  color: var(--cds-text-muted, #aaa);
  text-align: center;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.progress-step--done {
  color: var(--cds-primary);
  font-weight: 600;
}

/* ── Timeline ── */
.timeline-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.6rem;
}

.timeline-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
}

.timeline-icon {
  color: var(--cds-primary);
  margin-top: 0.15rem;
  flex-shrink: 0;
}

.timeline-date {
  display: block;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted, #888);
}

/* ── Fotos ── */
.photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(160px, 100%), 1fr));
  gap: 0.75rem;
}

.photo-item {
  margin: 0;
  display: grid;
  gap: 0.3rem;
}

.photo-item img {
  width: 100%;
  aspect-ratio: 4/3;
  object-fit: cover;
  border-radius: var(--cds-radius-md, 0.5rem);
  border: 1px solid var(--cds-border-soft);
}

.photo-item figcaption {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted, #888);
}

/* ── Notas ── */
.notes-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.75rem;
}

.notes-list li {
  border-left: 3px solid var(--cds-primary);
  padding-left: 0.75rem;
}

.notes-list p {
  margin: 0 0 0.2rem;
}
</style>
