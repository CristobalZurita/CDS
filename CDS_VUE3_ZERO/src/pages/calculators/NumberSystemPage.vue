<template>
  <BaseCalculatorPage title="Conversor de Sistemas Numéricos" description="Convierte y valida binario, decimal y hexadecimal en tiempo real.">
    <div class="calc-side-stack">
      <section class="calc-panel">
        <div class="panel-header">
          <div class="panel-title">
            <i class="fa-solid fa-hashtag"></i>
            Parámetros
          </div>
        </div>

        <div class="panel-body panel-form">
          <div class="helper-block">
            <p class="helper-title">Escribe en cualquiera de los tres campos y los otros dos se convierten al instante.</p>
          </div>

          <div class="number-system-live-grid">
            <BaseInput
              id="number-system-binary"
              :model-value="form.binary"
              :error="errors.binary"
              label="Binario"
              type="text"
              inputmode="numeric"
              placeholder="Ej: 101101"
              @update:modelValue="updateFrom('binary', $event)"
            />

            <BaseInput
              id="number-system-decimal"
              :model-value="form.decimal"
              :error="errors.decimal"
              label="Decimal"
              type="text"
              inputmode="numeric"
              placeholder="Ej: 45"
              @update:modelValue="updateFrom('decimal', $event)"
            />

            <BaseInput
              id="number-system-hexadecimal"
              :model-value="form.hexadecimal"
              :error="errors.hexadecimal"
              label="Hexadecimal"
              type="text"
              inputmode="text"
              placeholder="Ej: 2D"
              @update:modelValue="updateFrom('hexadecimal', $event)"
            />
          </div>

          <div class="form-actions">
            <BaseButton type="button" variant="ghost" class="reset-button" @click="reset">Resetear parámetros</BaseButton>
          </div>
        </div>
      </section>

      <section class="calc-panel output-panel">
        <div class="panel-header">
          <div class="panel-title">
            <i class="fa-solid fa-wave-square"></i>
            Resultado
          </div>
        </div>

        <div class="panel-body">
          <div v-if="isValid" class="output-values">
            <div v-for="row in summaryRows" :key="row.id" class="value-row">
              <span>{{ row.label }}</span>
              <strong>{{ row.value }}</strong>
            </div>
          </div>
          <p v-else class="result-hint">Ingresa un valor entero válido en binario, decimal o hexadecimal.</p>
        </div>
      </section>

      <section class="calc-panel output-panel">
        <div class="panel-header">
          <div class="panel-title">
            <i class="fa-solid fa-table-cells-large"></i>
            Tabla binaria
          </div>
        </div>

        <div class="panel-body">
          <div v-if="isValid" class="number-system-table-wrap">
            <table class="number-system-table">
              <thead>
                <tr>
                  <th>Bit</th>
                  <th>2^n</th>
                  <th>Valor posicional</th>
                  <th>Aporta</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in bitRows" :key="row.id">
                  <td>
                    <span class="number-system-bit" :class="{ 'number-system-bit--on': row.bit === '1' }">{{ row.bit }}</span>
                  </td>
                  <td>2^{{ row.exponent }}</td>
                  <td>{{ row.placeValue }}</td>
                  <td>{{ row.contribution }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="result-hint">La tabla se completa automáticamente cuando alguno de los tres campos es válido.</p>
        </div>
      </section>
    </div>

    <CalculatorReferencePanel
      image-path="/images/calculadoras/HEX.webp"
      alt="Referencia visual de sistemas numéricos binario hexadecimal y decimal"
    />
  </BaseCalculatorPage>
</template>

<script setup>
import CalculatorReferencePanel from '@/components/business/CalculatorReferencePanel.vue'
import { BaseCalculatorPage, BaseButton } from '@/components/base'
import { BaseInput } from '@/components/base'
import { useNumberSystemCalculator } from '@/composables/useNumberSystemCalculator'

const { bitRows, errors, form, isValid, reset, summaryRows, updateFrom } = useNumberSystemCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
<style scoped>
.number-system-live-grid {
  display: grid;
  gap: 0.85rem;
}

.number-system-table-wrap {
  overflow-x: auto;
}

.number-system-table {
  width: 100%;
  min-width: 28rem;
  border-collapse: collapse;
}

.number-system-table th,
.number-system-table td {
  padding: 0.7rem 0.8rem;
  border-bottom: 1px solid rgba(236, 107, 0, 0.12);
  text-align: left;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-normal);
  white-space: nowrap;
}

.number-system-table th {
  color: var(--cds-dark);
  font-weight: var(--cds-font-semibold);
}

.number-system-bit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2rem;
  min-height: 2rem;
  padding: 0 0.45rem;
  border-radius: 999px;
  border: 1px solid rgba(62, 60, 56, 0.18);
  background: rgba(62, 60, 56, 0.06);
  color: var(--cds-text-muted);
  font-weight: var(--cds-font-semibold);
}

.number-system-bit--on {
  border-color: rgba(236, 107, 0, 0.26);
  background: rgba(236, 107, 0, 0.14);
  color: var(--cds-primary);
}

@media (min-width: 640px) {
  .number-system-live-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
