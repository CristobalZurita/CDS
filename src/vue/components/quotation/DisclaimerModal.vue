<template>
  <Transition name="fade">
    <div v-if="show" class="disclaimer-overlay">
      <div class="disclaimer-modal" @click.stop>
        <!-- Header -->
        <div class="disclaimer-header">
          <span class="warning-icon">⚠️</span>
          <h2>IMPORTANTE - LEA ANTES DE CONTINUAR</h2>
          <button @click="$emit('cancel')" class="close-btn">&times;</button>
        </div>

        <!-- Content -->
        <div class="disclaimer-content">
          <p class="highlight">
            Esta cotización es <strong>INDICATIVA</strong> y <strong>NO VINCULANTE</strong>.
          </p>

          <ul class="disclaimer-list">
            <li>
              El precio final se confirma tras revisión presencial del equipo en nuestro taller.
            </li>
            <li>
              El diagnóstico completo requiere abrir el instrumento, lo que puede revelar fallas
              adicionales no detectables externamente.
            </li>
            <li>
              El presupuesto formal tiene un costo de <strong>$20.000 CLP</strong>, que es:
              <ul class="sub-list">
                <li><strong>ABONABLE:</strong> Se descuenta del total si decide reparar</li>
                <li><strong>NO REEMBOLSABLE:</strong> Queda como pago por diagnóstico si rechaza</li>
              </ul>
            </li>
            <li>
              <strong>Compromiso CDS:</strong> Nunca cobramos más del 50% del valor de mercado
              actual del instrumento.
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
                He leído y acepto las condiciones anteriores
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
            Continuar y Ver Cotización →
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
