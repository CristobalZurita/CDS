<template>
  <section>
    <h1>SmdCapacitor Calculator</h1>
    <form @submit.prevent="onCalculate">
      <pre>Inputs definidos por contrato</pre>
      <button type="submit">Calculate</button>
    </form>

    <div v-if="result">
      <pre v-if="result.state === 'OK'">{{ result.value }}</pre>
      <ul v-if="result.errors">
        <li v-for="e in result.errors" :key="e">{{ e }}</li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { useCalculator } from '@/composables/useCalculator';
import { SmdCapacitorInput } from '@/domain/smdCapacitor/contract';
import { calculateSmdCapacitor } from '@/domain/smdCapacitor/model';
import { createValidationResult } from '@/validation';

const input = reactive<SmdCapacitorInput>({} as SmdCapacitorInput);

function validator() {
  return createValidationResult();
}

const { result, calculate } = useCalculator(validator, calculateSmdCapacitor);

function onCalculate() {
  calculate(input);
}
</script>
