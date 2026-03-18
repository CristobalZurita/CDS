<template>
  <section class="calc-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-sliders"></i>
        Parametros
      </div>
    </div>

    <div class="panel-body">
      <div class="form-grid">
        <div class="form-field">
          <label>R</label>
          <div class="unit-input">
            <input v-model.number="form.r_value" type="number" min="0" step="0.1" inputmode="decimal" />
            <select v-model="form.r_unit" class="unit-select">
              <option value="ohm">Ohm</option>
              <option value="kohm">kOhm</option>
              <option value="mohm">MOhm</option>
            </select>
          </div>
        </div>

        <div class="form-field">
          <label>C</label>
          <div class="unit-input">
            <input v-model.number="form.c_value" type="number" min="0" step="0.1" inputmode="decimal" />
            <select v-model="form.c_unit" class="unit-select">
              <option value="pf">pF</option>
              <option value="nf">nF</option>
              <option value="uf">µF</option>
            </select>
          </div>
        </div>

        <div class="form-field">
          <label>Vcc (V)</label>
          <input v-model.number="form.vcc_v" type="number" min="0" step="0.1" inputmode="decimal" class="input-solo" />
        </div>
      </div>

      <div class="form-actions">
        <button type="button" class="action-btn" @click="$emit('reset')">
          <i class="fa-solid fa-rotate-left"></i>
          Resetear parametros
        </button>
      </div>

      <div class="pinout-card">
        <img :src="pinoutSrc" alt="Pinout CD40106" class="pinout-image" />
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  form: { type: Object, required: true },
  pinoutSrc: { type: String, default: '' }
})

defineEmits(['reset'])
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
<style scoped src="./cd40106PageShared.css"></style>
