<template>
  <section class="calc-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-palette"></i>
        Parametros
      </div>
      <div class="panel-tabs">
        <button
          v-for="bands in [4, 5, 6]"
          :key="bands"
          type="button"
          class="panel-tab"
          :class="{ 'panel-tab--active': form.bands === bands }"
          @click="$emit('apply-bands', bands)"
        >
          {{ bands }} bandas
        </button>
      </div>
    </div>

    <div class="panel-body">
      <div class="form-grid">
        <label class="form-field">
          <span>1ra banda</span>
          <select v-model="form.colors[0]">
            <option v-for="color in digitColorOptions" :key="`d1-${color.value}`" :value="color.value">
              {{ color.label }}
            </option>
          </select>
        </label>

        <label class="form-field">
          <span>2da banda</span>
          <select v-model="form.colors[1]">
            <option v-for="color in digitColorOptions" :key="`d2-${color.value}`" :value="color.value">
              {{ color.label }}
            </option>
          </select>
        </label>

        <label v-if="form.bands >= 5" class="form-field">
          <span>3ra banda</span>
          <select v-model="form.colors[2]">
            <option v-for="color in digitColorOptions" :key="`d3-${color.value}`" :value="color.value">
              {{ color.label }}
            </option>
          </select>
        </label>

        <label class="form-field">
          <span>Multiplicador</span>
          <select v-model="form.colors[multiplierIndex]">
            <option v-for="color in multiplierColorOptions" :key="`m-${color.value}`" :value="color.value">
              {{ color.label }}
            </option>
          </select>
        </label>

        <label class="form-field">
          <span>Tolerancia</span>
          <select v-model="form.colors[toleranceIndex]">
            <option v-for="color in toleranceColorOptions" :key="`t-${color.value}`" :value="color.value">
              {{ color.label }}
            </option>
          </select>
        </label>

        <label v-if="form.bands === 6" class="form-field">
          <span>Tempco</span>
          <select v-model="form.colors[tempcoIndex]">
            <option v-for="color in tempcoColorOptions" :key="`tc-${color.value}`" :value="color.value">
              {{ color.label }}
            </option>
          </select>
        </label>
      </div>

      <div class="form-actions">
        <button type="button" class="action-btn" @click="$emit('reset-bands')">
          <i class="fa-solid fa-rotate-left"></i>
          Resetear parametros
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  digitColorOptions: { type: Array, required: true },
  form: { type: Object, required: true },
  multiplierColorOptions: { type: Array, required: true },
  multiplierIndex: { type: Number, required: true },
  tempcoColorOptions: { type: Array, required: true },
  tempcoIndex: { type: Number, required: true },
  toleranceColorOptions: { type: Array, required: true },
  toleranceIndex: { type: Number, required: true }
})

defineEmits(['apply-bands', 'reset-bands'])
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
