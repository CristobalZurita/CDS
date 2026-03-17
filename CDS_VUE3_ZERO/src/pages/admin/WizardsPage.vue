<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Wizards</h1>
        <p>Atajos de operacion y generacion de links para firma/foto.</p>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>
    <p v-if="success" class="admin-success">{{ success }}</p>

    <section class="cards-grid">
      <article v-for="card in cards" :key="card.id" class="wizard-card">
        <h2>{{ card.title }}</h2>
        <p>{{ card.description }}</p>
        <button class="btn-primary" @click="openWizard(card)">{{ card.cta }}</button>
      </article>
    </section>

    <section class="panel-card">
      <h2>Wizard rapido: firma OT</h2>
      <div class="form-grid two-cols">
        <label><span>Repair ID *</span><input v-model.number="signatureForm.repair_id" type="number" min="1" /></label>
        <label>
          <span>Tipo</span>
          <select v-model="signatureForm.request_type">
            <option value="ingreso">ingreso</option>
            <option value="retiro">retiro</option>
          </select>
        </label>
      </div>
      <div class="panel-actions">
        <button class="btn-primary" :disabled="loading" @click="requestSignatureLink">
          {{ loading ? 'Generando...' : 'Generar link de firma' }}
        </button>
      </div>
      <p v-if="signatureLink" class="link-line"><strong>Link:</strong> <a :href="signatureLink" target="_blank" rel="noopener">{{ signatureLink }}</a></p>
    </section>

    <section class="panel-card">
      <h2>Wizard rapido: foto cliente</h2>
      <div class="form-grid two-cols">
        <label><span>Repair ID *</span><input v-model.number="photoRequestForm.repair_id" type="number" min="1" /></label>
        <label>
          <span>Tipo</span>
          <select v-model="photoRequestForm.photo_type">
            <option value="client">client</option>
            <option value="general">general</option>
            <option value="damage">damage</option>
          </select>
        </label>
      </div>
      <div class="panel-actions">
        <button class="btn-primary" :disabled="loading" @click="requestPhotoLink">
          {{ loading ? 'Generando...' : 'Generar link de foto' }}
        </button>
      </div>
      <p v-if="photoLink" class="link-line"><strong>Link:</strong> <a :href="photoLink" target="_blank" rel="noopener">{{ photoLink }}</a></p>
    </section>
  </main>
</template>

<script setup>
import { useWizardsPage } from '@/composables/useWizardsPage'

const {
  cards,
  loading,
  error,
  success,
  signatureForm,
  photoRequestForm,
  signatureLink,
  photoLink,
  openWizard,
  requestSignatureLink,
  requestPhotoLink
} = useWizardsPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped>
.wizard-card { padding: .9rem; display: grid; gap: .55rem; }
.wizard-card h2 { margin: 0; font-size: var(--cds-text-xl); }
.wizard-card p { margin: 0; color: var(--cds-text-muted); }
.cards-grid { gap: .75rem; }
.link-line { margin: 0; word-break: break-all; }
@media (min-width: 900px) { .cards-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
</style>
