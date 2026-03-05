<template>
  <Transition name="fade">
      <div v-if="show" class="disclaimer-overlay">
      <div class="disclaimer-modal" @click.stop>
        <!-- Header -->
        <div class="disclaimer-header">
          <span class="warning-icon">⚠️</span>
          <h2>IMPORTANTE - ESTIMACIÓN REFERENCIAL</h2>
        </div>

        <!-- Content -->
        <div class="disclaimer-content">
          <p class="highlight">
            Esta cotización es <strong>INDICATIVA</strong> y <strong>NO VINCULANTE</strong>.
          </p>

          <ul class="disclaimer-list">
            <li>
              El valor mostrado es sólo una referencia preliminar obtenida desde información visible y respuestas del usuario.
            </li>
            <li>
              El diagnóstico real requiere revisión física en taller y puede revelar fallas adicionales o causas distintas.
            </li>
            <li>
              El rango puede cambiar según tamaño del equipo, controles, síntomas acumulados y daños no visibles externamente.
            </li>
            <li>
              Esta pantalla no representa una promesa comercial ni un presupuesto formal definitivo.
            </li>
          </ul>

          <!-- Acceptance Checkbox -->
          <div class="acceptance-section">
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="accepted"
                class="checkbox-input"
              />
              <span class="checkbox-text">
                Entiendo que esta estimación es sólo referencial y no representa el valor final real
              </span>
            </label>
          </div>
        </div>

        <!-- Actions -->
        <div class="disclaimer-actions">
          <button @click="$emit('cancel')" class="btn-cancel">
            ← Volver
          </button>
          <button
            @click="$emit('accept')"
            :disabled="!accepted"
            class="btn-accept"
            :class="{ 'btn-accept--disabled': !accepted }"
          >
            Continuar y Ver Estimación →
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  show: {
    type: Boolean,
    required: true
  }
})

defineEmits(['accept', 'cancel'])

const accepted = ref(false)
</script>
