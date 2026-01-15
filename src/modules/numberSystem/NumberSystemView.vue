<template>
  <section>
    <h1>NumberSystem Calculator</h1>
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
import { NumberSystemInput } from '@/domain/numberSystem/contract';
import { convertNumberSystem } from '@/domain/numberSystem/model';
import { createValidationResult } from '@/validation';

const input = reactive<NumberSystemInput>({} as NumberSystemInput);

function validator() {
  return createValidationResult();
}

const { result, calculate } = useCalculator(validator, convertNumberSystem);

function onCalculate() {
  calculate(input);
}
</script>
