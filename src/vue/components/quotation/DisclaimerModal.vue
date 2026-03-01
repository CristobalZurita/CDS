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

<style lang="scss" scoped>
@use '@/scss/core' as *;

/* Overlay */
.disclaimer-overlay {
  position: fixed;
  inset: 0;
  background: rgba($color-black, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: $z-index-dropdown;
  padding: $spacer-md;
  overflow-y: auto;
}

/* Modal */
.disclaimer-modal {
  background: $color-black;
  color: $color-warning;
  border-radius: $border-radius-lg;
  max-width: 700px;
  width: 100%;
  box-shadow: 0 0 0 6px $color-warning, 0 18px 50px rgba($color-black, 0.6);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow-y: auto;
}

/* Header */
.disclaimer-header {
  display: flex;
  align-items: flex-start;
  gap: $spacer-md;
  padding: $spacer-xl;
  border-bottom: 4px solid $color-black;
  position: sticky;
  top: 0;
  background: $color-warning;
  z-index: 1;
}

.warning-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
  line-height: $lh-none;
}

.disclaimer-header h2 {
  margin: 0;
  color: $color-black;
  font-size: $text-xl;
  flex: 1;
}

.close-btn {
  background: $color-black;
  border: 2px solid $color-black;
  font-size: $spacer-xl;
  cursor: pointer;
  color: $color-warning;
  padding: 0;
  width: $spacer-xl;
  height: $spacer-xl;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: $border-radius-sm;
  transition: $transition-fast;
}

.close-btn:hover {
  background-color: $color-danger;
  color: $color-white;
}

/* Content */
.disclaimer-content {
  padding: $spacer-xl;
  flex: 1;
  overflow-y: auto;
}

.highlight {
  background: $color-warning;
  border-left: 6px solid $color-danger;
  padding: $spacer-md;
  margin-bottom: $spacer-lg;
  border-radius: $border-radius-sm;
  font-size: $text-md;
  line-height: $lh-relaxed;
}

.highlight strong {
  color: $color-black;
  font-weight: $fw-bold;
}

.disclaimer-list {
  list-style: none;
  padding: 0;
  margin: 0 0 $spacer-xl 0;
}

.disclaimer-list > li {
  margin-bottom: 1.25rem;
  padding-left: 1.75rem;
  position: relative;
  line-height: $lh-relaxed;
  color: $color-warning;
}

.disclaimer-list > li:before {
  content: '✖';
  position: absolute;
  left: 0;
  color: $color-danger;
  font-weight: $fw-bold;
  font-size: $text-xl;
}

.sub-list {
  list-style: none;
  padding: $spacer-sm 0 0 $spacer-md;
  margin: $spacer-sm 0 0 0;
}

.sub-list li {
  margin: $spacer-sm 0;
  font-size: $text-sm;
  color: $color-warning;
}

.sub-list li strong {
  color: $color-warning;
}

/* Acceptance */
.acceptance-section {
  margin-top: $spacer-xl;
  padding: $spacer-md;
  background: $color-warning;
  border-radius: $border-radius-md;
  border: 3px solid $color-black;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  user-select: none;
}

.checkbox-input {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: $color-danger;
  flex-shrink: 0;
}

.checkbox-text {
  color: $color-black;
  font-weight: $fw-bold;
}

/* Actions */
.disclaimer-actions {
  display: flex;
  justify-content: space-between;
  gap: $spacer-md;
  padding: $spacer-xl;
  border-top: 4px solid $color-warning;
  background: $color-black;
  position: sticky;
  bottom: 0;
}

.btn-cancel,
.btn-accept {
  padding: 0.875rem 1.75rem;
  border-radius: $border-radius-md;
  font-size: $text-base;
  font-weight: $fw-semibold;
  cursor: pointer;
  border: none;
  transition: $transition-fast;
  flex: 1;
}

.btn-cancel {
  background: transparent;
  border: 2px solid $color-warning;
  color: $color-warning;
}

.btn-cancel:hover {
  background: $color-warning;
  border-color: $color-warning;
  color: $color-black;
}

.btn-accept {
  background: $color-danger;
  color: $color-white;
  box-shadow: 0 4px 12px rgba($color-danger, 0.4);
}

.btn-accept:hover:not(:disabled) {
  background: darken($color-danger, 8%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba($color-danger, 0.5);
}

.btn-accept:active:not(:disabled) {
  transform: translateY(0);
}

.btn-accept--disabled,
.btn-accept:disabled {
  background: $color-black;
  cursor: not-allowed;
  box-shadow: none;
  border: 2px solid $color-warning;
  color: $color-warning;
  opacity: 0.6;
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: $transition-base;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@include media-breakpoint-down(sm) {
  .disclaimer-overlay {
    padding: $spacer-sm;
  }

  .disclaimer-modal {
    border-radius: $border-radius-md;
    max-height: 95vh;
  }

  .disclaimer-header {
    padding: $spacer-lg;
    gap: 0.75rem;
  }

  .disclaimer-header h2 {
    font-size: $text-lg;
  }

  .warning-icon {
    font-size: $spacer-xl;
  }

  .disclaimer-content {
    padding: $spacer-lg;
  }

  .highlight {
    padding: 0.75rem;
  }

  .disclaimer-actions {
    flex-direction: column;
    padding: $spacer-lg;
  }

  .btn-cancel,
  .btn-accept {
    padding: 0.75rem $spacer-lg;
    font-size: $text-sm;
  }
}
</style>
