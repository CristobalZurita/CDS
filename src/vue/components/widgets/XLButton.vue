<template>
    <button class="btn btn-primary btn-xl"
                :type="props.type || 'button'"
                :class="[props.class, variant && `btn-${variant}`]"
                @click="props.action ? props.action() : null"
                v-if="props.label || props.action || props.type === 'submit'">
        <i class="me-2" :class="props.icon"/>
        <span v-html="props.label"/>
    </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    class: String,
    label: String,
    type: String,
    icon: String,
    variant: String, // 'orange', 'outline', etc.
    action: Function
})

const variant = computed(() => props.variant)
</script>
