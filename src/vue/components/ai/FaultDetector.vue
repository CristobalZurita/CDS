<template>
  <div class="fault-detector">
    <label v-for="fault in faults" :key="fault.code" class="fault">
      <input
        type="checkbox"
        :value="fault.code"
        :checked="modelValue.includes(fault.code)"
        @change="toggle(fault.code)"
      />
      <span>{{ fault.label || fault.name || fault.code }}</span>
    </label>
  </div>
</template>

<script setup>
const props = defineProps({
  faults: { type: Array, default: () => [] },
  modelValue: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue'])

const toggle = (code) => {
  const next = props.modelValue.includes(code)
    ? props.modelValue.filter((item) => item !== code)
    : [...props.modelValue, code]
  emit('update:modelValue', next)
}
</script>

<style scoped lang="scss">
@import '@/scss/_core.scss';

.fault-detector {
  display: grid;
  gap: 0.5rem;
}
.fault {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
