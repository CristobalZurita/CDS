<template>
  <NeoDashActiveSection
    eyebrow="Appointments"
    title="Agenda y diagnostico"
    description="Entrada rápida al flujo real de disponibilidad, confirmacion y reserva de cita."
  >
    <template #actions>
      <router-link class="neo-dash-inline-link" to="/agendar">Abrir agenda completa</router-link>
    </template>

    <div class="neo-dash-grid">
      <article class="neo-dash-card">
        <h3 class="neo-dash-card-title">Cómo funciona</h3>
        <div class="neo-dash-list">
          <article class="neo-dash-item">
            <h4 class="neo-dash-item-title">1. Elige fecha</h4>
            <p class="neo-dash-item-copy">Se consulta disponibilidad real desde el sistema actual.</p>
          </article>
          <article class="neo-dash-item">
            <h4 class="neo-dash-item-title">2. Selecciona horario</h4>
            <p class="neo-dash-item-copy">Los bloques ocupados se validan antes de confirmar.</p>
          </article>
          <article class="neo-dash-item">
            <h4 class="neo-dash-item-title">3. Confirma cita</h4>
            <p class="neo-dash-item-copy">La reserva se registra sobre el flujo real ya vivo en CDS.</p>
          </article>
        </div>
      </article>

      <article class="neo-dash-callout">
        <h3 class="neo-dash-callout-title">Acceso rápido</h3>
        <p class="neo-dash-callout-copy">
          La agenda sigue funcionando como página dedicada. Desde el dashboard entra como atajo operativo.
        </p>
        <div class="neo-dash-inline-actions">
          <router-link class="neo-dash-link-btn neo-dash-link-btn--primary" to="/agendar">
            <i class="fa-solid fa-calendar-check"></i>
            Agendar revisión
          </router-link>
          <router-link class="neo-dash-link-btn neo-dash-link-btn--secondary" to="/cotizador">
            <i class="fa-solid fa-plus"></i>
            Nueva cotización
          </router-link>
        </div>
      </article>
    </div>
  </NeoDashActiveSection>
</template>

<script setup>
import NeoDashActiveSection from './NeoDashActiveSection.vue'
</script>

<style src="./neoDashboardShared.css"></style>
