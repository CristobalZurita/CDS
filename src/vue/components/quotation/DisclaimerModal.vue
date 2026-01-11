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

<style scoped>
/* Overlay */
.disclaimer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  overflow-y: auto;
}

/* Modal */
.disclaimer-modal {
  background: white;
  border-radius: 12px;
  max-width: 700px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow-y: auto;
}

/* Header */
.disclaimer-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 2rem;
  border-bottom: 2px solid #fee;
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
}

.warning-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
  line-height: 1;
}

.disclaimer-header h2 {
  margin: 0;
  color: #c53030;
  font-size: 1.25rem;
  flex: 1;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: #f5f5f5;
  color: #333;
}

/* Content */
.disclaimer-content {
  padding: 2rem;
  flex: 1;
  overflow-y: auto;
}

.highlight {
  background: linear-gradient(135deg, #fff5f5, #ffe8e8);
  border-left: 4px solid #c53030;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border-radius: 4px;
  font-size: 1.05rem;
  line-height: 1.6;
}

.highlight strong {
  color: #c53030;
  font-weight: 700;
}

.disclaimer-list {
  list-style: none;
  padding: 0;
  margin: 0 0 2rem 0;
}

.disclaimer-list > li {
  margin-bottom: 1.25rem;
  padding-left: 1.75rem;
  position: relative;
  line-height: 1.6;
  color: #333;
}

.disclaimer-list > li:before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #2f855a;
  font-weight: bold;
  font-size: 1.25rem;
}

.sub-list {
  list-style: none;
  padding: 0.5rem 0 0 1rem;
  margin: 0.5rem 0 0 0;
}

.sub-list li {
  margin: 0.5rem 0;
  font-size: 0.95rem;
  color: #555;
}

.sub-list li strong {
  color: #2d3748;
}

/* Acceptance */
.acceptance-section {
  margin-top: 2rem;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 8px;
  border: 1px solid #cbd5e0;
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
  accent-color: #2f855a;
  flex-shrink: 0;
}

.checkbox-text {
  color: #2d3748;
  font-weight: 500;
}

/* Actions */
.disclaimer-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid #e2e8f0;
  background: #f9fafb;
  position: sticky;
  bottom: 0;
}

.btn-cancel,
.btn-accept {
  padding: 0.875rem 1.75rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  flex: 1;
}

.btn-cancel {
  background: white;
  border: 2px solid #cbd5e0;
  color: #4a5568;
}

.btn-cancel:hover {
  background: #edf2f7;
  border-color: #a0aec0;
}

.btn-accept {
  background: linear-gradient(135deg, #2f855a, #276749);
  color: white;
  box-shadow: 0 4px 12px rgba(47, 133, 90, 0.3);
}

.btn-accept:hover:not(:disabled) {
  background: linear-gradient(135deg, #276749, #22543d);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(47, 133, 90, 0.4);
}

.btn-accept:active:not(:disabled) {
  transform: translateY(0);
}

.btn-accept--disabled,
.btn-accept:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
  box-shadow: none;
  opacity: 0.6;
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 640px) {
  .disclaimer-overlay {
    padding: 0.5rem;
  }

  .disclaimer-modal {
    border-radius: 8px;
    max-height: 95vh;
  }

  .disclaimer-header {
    padding: 1.5rem;
    gap: 0.75rem;
  }

  .disclaimer-header h2 {
    font-size: 1.1rem;
  }

  .warning-icon {
    font-size: 2rem;
  }

  .disclaimer-content {
    padding: 1.5rem;
  }

  .highlight {
    padding: 0.75rem;
  }

  .disclaimer-actions {
    flex-direction: column;
    padding: 1.5rem;
  }

  .btn-cancel,
  .btn-accept {
    padding: 0.75rem 1.5rem;
    font-size: 0.95rem;
  }
}
</style>
