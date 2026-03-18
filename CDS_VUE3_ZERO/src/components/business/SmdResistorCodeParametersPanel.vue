<template>
  <section class="calc-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-hashtag"></i>
        Parametros
      </div>
    </div>

    <div class="panel-body">
      <div class="form-grid">
        <label class="form-field">
          <span>Codigo SMD</span>
          <input v-model.trim="form.code" type="text" placeholder="Ej: 103, 1001, 01C, 4R7" />
        </label>

        <label class="form-field">
          <span>Formato</span>
          <select v-model="form.type">
            <option v-for="item in smdResistorTypeOptions" :key="item.value" :value="item.value">
              {{ item.label }}
            </option>
          </select>
        </label>
      </div>

      <div class="helper-block">
        <p class="helper-title">Ejemplos rapidos</p>
        <div class="example-list">
          <button
            v-for="example in activeExamples"
            :key="example"
            type="button"
            class="example-chip"
            @click="applyExample(example)"
          >
            {{ example }}
          </button>
        </div>
      </div>

      <div class="helper-block">
        <p class="helper-title">Notacion R</p>
        <div class="example-list">
          <button type="button" class="example-chip" @click="applyExample('4R7')">4R7</button>
          <button type="button" class="example-chip" @click="applyExample('R47')">R47</button>
          <button type="button" class="example-chip" @click="applyExample('R604')">R604</button>
        </div>
      </div>

      <div class="form-actions">
        <button type="button" class="action-btn" @click="$emit('reset')">
          <i class="fa-solid fa-rotate-left"></i>
          Resetear parametros
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  activeExamples: { type: Array, required: true },
  applyExample: { type: Function, required: true },
  form: { type: Object, required: true },
  smdResistorTypeOptions: { type: Array, required: true }
})

defineEmits(['reset'])
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
