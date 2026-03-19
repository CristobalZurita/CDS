<template>
  <section class="calc-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-scale-balanced"></i>
        Conversion de unidades
      </div>
    </div>

    <div class="panel-body">
      <div class="diagram-card cap-visual-card">
        <img
          class="cap-visual-card__image cap-visual-card__image--electrolytic"
          src="/images/calculadoras/CAP_E.webp"
          alt="Capacitor electrolitico"
        />
      </div>
      <p class="cap-visual-caption">Electrolitico (Cap E)</p>

      <div class="form-grid form-grid-wide">
        <label class="form-field">
          <span>Picofarad</span>
          <div class="unit-input">
            <input v-model.number="form.pf" type="number" min="0" step="0.1" @input="convertFrom('pf')" />
            <span class="unit-tag">pF</span>
          </div>
        </label>

        <label class="form-field">
          <span>Nanofarad</span>
          <div class="unit-input">
            <input v-model.number="form.nf" type="number" min="0" step="0.1" @input="convertFrom('nf')" />
            <span class="unit-tag">nF</span>
          </div>
        </label>

        <label class="form-field">
          <span>Microfarad</span>
          <div class="unit-input">
            <input v-model.number="form.uf" type="number" min="0" step="0.1" @input="convertFrom('uf')" />
            <span class="unit-tag">µF</span>
          </div>
        </label>

        <label class="form-field">
          <span>Farad</span>
          <div class="unit-input">
            <input v-model.number="form.f" type="number" min="0" step="0.1" @input="convertFrom('f')" />
            <span class="unit-tag">F</span>
          </div>
        </label>
      </div>

      <div class="form-actions">
        <button type="button" class="action-btn" @click="$emit('reset-conversion')">
          <i class="fa-solid fa-rotate-left"></i>
          Resetear parametros
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  convertFrom: { type: Function, required: true },
  form: { type: Object, required: true }
})

defineEmits(['reset-conversion'])
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
<style scoped src="./smdCapacitorPageShared.css"></style>
