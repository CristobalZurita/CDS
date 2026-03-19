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
        <div class="form-field">
          <span>1ra banda</span>
          <ResistorColorSelect
            :model-value="form.colors[0]"
            :options="digitColorOptions"
            :neutral="!fieldTouched[0]"
            @update:modelValue="updateColor(0, $event)"
          />
        </div>

        <div class="form-field">
          <span>2da banda</span>
          <ResistorColorSelect
            :model-value="form.colors[1]"
            :options="digitColorOptions"
            :neutral="!fieldTouched[1]"
            @update:modelValue="updateColor(1, $event)"
          />
        </div>

        <div v-if="form.bands >= 5" class="form-field">
          <span>3ra banda</span>
          <ResistorColorSelect
            :model-value="form.colors[2]"
            :options="digitColorOptions"
            :neutral="!fieldTouched[2]"
            @update:modelValue="updateColor(2, $event)"
          />
        </div>

        <div class="form-field">
          <span>Multiplicador</span>
          <ResistorColorSelect
            :model-value="form.colors[multiplierIndex]"
            :options="multiplierColorOptions"
            :neutral="!fieldTouched[multiplierIndex]"
            @update:modelValue="updateColor(multiplierIndex, $event)"
          />
        </div>

        <div class="form-field">
          <span>Tolerancia</span>
          <ResistorColorSelect
            :model-value="form.colors[toleranceIndex]"
            :options="toleranceColorOptions"
            :neutral="!fieldTouched[toleranceIndex]"
            @update:modelValue="updateColor(toleranceIndex, $event)"
          />
        </div>

        <div v-if="form.bands === 6" class="form-field">
          <span>Tempco</span>
          <ResistorColorSelect
            :model-value="form.colors[tempcoIndex]"
            :options="tempcoColorOptions"
            :neutral="!fieldTouched[tempcoIndex]"
            @update:modelValue="updateColor(tempcoIndex, $event)"
          />
        </div>
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
import { reactive, watch } from 'vue'
import ResistorColorSelect from '@/components/business/ResistorColorSelect.vue'

const props = defineProps({
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

const fieldTouched = reactive([false, false, false, false, false, false])

watch(() => props.form.bands, () => {
  fieldTouched.fill(false)
})

function updateColor(index, value) {
  props.form.colors[index] = value
  fieldTouched[index] = true
}
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
