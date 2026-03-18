<template>
  <article class="timer555-panel">
    <header class="panel-header">
      <h2 class="panel-title">
        <i class="fa-solid fa-sliders"></i>
        Parametros
      </h2>

      <div class="panel-tabs" role="tablist" aria-label="Modo de funcionamiento">
        <button
          v-for="option in timer555ModeOptions"
          :key="option.value"
          type="button"
          class="panel-tab"
          :class="{ 'panel-tab--active': form.mode === option.value }"
          @click="form.mode = option.value"
        >
          {{ option.label }}
        </button>
      </div>
    </header>

    <div class="panel-form">
      <div class="form-grid">
        <div class="form-field" v-if="isAstable">
          <label>R1</label>
          <div class="unit-input">
            <input v-model.number="form.r1_value" type="number" min="0" step="0.1" inputmode="decimal" />
            <select v-model="form.r1_unit" class="unit-select">
              <option value="ohm">Ω</option>
              <option value="kohm">kΩ</option>
              <option value="mohm">MΩ</option>
            </select>
          </div>
        </div>

        <div class="form-field" v-if="isAstable">
          <label>R2</label>
          <div class="unit-input">
            <input v-model.number="form.r2_value" type="number" min="0" step="0.1" inputmode="decimal" />
            <select v-model="form.r2_unit" class="unit-select">
              <option value="ohm">Ω</option>
              <option value="kohm">kΩ</option>
              <option value="mohm">MΩ</option>
            </select>
          </div>
        </div>

        <div class="form-field" v-if="isMonostable">
          <label>R</label>
          <div class="unit-input">
            <input v-model.number="form.r_value" type="number" min="0" step="0.1" inputmode="decimal" />
            <select v-model="form.r_unit" class="unit-select">
              <option value="ohm">Ω</option>
              <option value="kohm">kΩ</option>
              <option value="mohm">MΩ</option>
            </select>
          </div>
        </div>

        <div class="form-field" v-if="!isBistable">
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
          <input
            v-model.number="form.vcc_v"
            type="number"
            min="0"
            step="0.1"
            inputmode="decimal"
            class="input-solo"
            :disabled="isBistable"
          />
        </div>
      </div>

      <div class="mode-hint" v-if="isBistable">
        <i class="fa-solid fa-circle-info"></i>
        En biestable la salida se alterna por disparo SET/RESET. Vcc se fija en 5V para evitar inconsistencias.
      </div>

      <div class="form-actions">
        <button type="button" class="btn-reset" @click="$emit('reset')">
          <i class="fa-solid fa-rotate-left"></i>
          Resetear parametros
        </button>
      </div>

      <section class="pinout-card">
        <img src="/images/calculadoras/555_Pinout.webp" alt="Pinout NE555" class="pinout-image" />
      </section>
    </div>
  </article>
</template>

<script setup>
defineProps({
  form: { type: Object, required: true },
  isAstable: { type: Boolean, default: false },
  isBistable: { type: Boolean, default: false },
  isMonostable: { type: Boolean, default: false },
  timer555ModeOptions: { type: Array, required: true }
})

defineEmits(['reset'])
</script>

<style scoped src="../../pages/calculators/Timer555Page.css"></style>
