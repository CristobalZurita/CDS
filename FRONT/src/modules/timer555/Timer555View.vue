<template>
  <section>
    <h1>NE555 Timer Calculator</h1>

    <form @submit.prevent="onCalculate">
      <label>
        Mode
        <select v-model="input.mode">
          <option value="monostable">Monostable</option>
          <option value="astable_standard">Astable</option>
        </select>
      </label>

      <label v-if="input.mode === 'monostable'">
        R (Ω)
        <input type="number" v-model.number="input.R_ohm" />
      </label>

      <label v-if="input.mode === 'astable_standard'">
        R1 (Ω)
        <input type="number" v-model.number="input.R1_ohm" />
      </label>

      <label v-if="input.mode === 'astable_standard'">
        R2 (Ω)
        <input type="number" v-model.number="input.R2_ohm" />
      </label>

      <label>
        C (F)
        <input type="number" v-model.number="input.C_farad" />
      </label>

      <label>
        Vcc (V)
        <input type="number" v-model.number="input.Vcc_volt" />
      </label>

      <button type="submit">Calculate</button>
    </form>

    <div v-if="result">
      <h2>Result</h2>

      <pre v-if="result.state === 'OK'">
{{ result.value }}
      </pre>

      <ul v-if="result.errors">
        <li v-for="e in result.errors" :key="e">{{ e }}</li>
      </ul>

      <ul v-if="result.warnings">
        <li v-for="w in result.warnings" :key="w">{{ w }}</li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { useCalculator } from '@/composables/useCalculator';
import { Timer555Input } from '@/domain/timer555/contract';
import { calculateTimer555 } from '@/domain/timer555/model';
import { createValidationResult } from '@/validation';
import { validateCapacitance, validateResistance, validateVoltage } from '@/validation/physical';

const input = reactive<Timer555Input>({
  mode: 'monostable',
  C_farad: 0,
  Vcc_volt: 5
});

function validator(i: Timer555Input) {
  const result = createValidationResult();

  if (i.C_farad !== undefined) {
    const e = validateCapacitance(i.C_farad);
    if (e) result.errors.push(e);
  }

  if (i.Vcc_volt !== undefined) {
    const e = validateVoltage(i.Vcc_volt);
    if (e) result.errors.push(e);
  }

  if (i.mode === 'monostable' && i.R_ohm !== undefined) {
    const e = validateResistance(i.R_ohm);
    if (e) result.errors.push(e);
  }

  if (i.mode === 'astable_standard') {
    if (i.R1_ohm !== undefined) {
      const e = validateResistance(i.R1_ohm);
      if (e) result.errors.push(e);
    }
    if (i.R2_ohm !== undefined) {
      const e = validateResistance(i.R2_ohm);
      if (e) result.errors.push(e);
    }
  }

  if (result.errors.length > 0) {
    result.valid = false;
  }

  return result;
}

const { result, calculate } = useCalculator(validator, calculateTimer555);

function onCalculate() {
  calculate(input);
}
</script>
