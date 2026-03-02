<template>
    <div class="progress-bar-wrapper" :class="props.class">
        <div class="progress">
            <div class="progress-bar"
                 role="progressbar"
                 :class="progressClass"
                 :aria-valuenow="parsedPercentage"
                 aria-valuemin="0"
                 aria-valuemax="100"/>
        </div>
    </div>
</template>

<script setup>
import {useUtils} from "/src/composables/utils.js"
import {computed} from "vue"

const utils = useUtils()

const props = defineProps({
    class: String,
    percentage: Number
})

const parsedPercentage = computed(() => {
    return utils.clamp(props.percentage, 0, 100)
})

const progressClass = computed(() => {
    return `progress-${Math.round(parsedPercentage.value)}`
})
</script>
