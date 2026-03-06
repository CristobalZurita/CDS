<template>
    <div class="progress-bar-wrapper" :class="props.class">
        <div class="progress-container" :style="containerStyles">
            <div class="progress-bar"
                 :class="barClasses"
                 role="progressbar"
                 :style="barStyles"
                 :aria-valuenow="parsedPercentage"
                 aria-valuemin="0"
                 aria-valuemax="100"/>
        </div>
    </div>
</template>

<script setup>
import { useUtils } from "/src/composables/utils.js"
import { computed } from "vue"
import { COLORS } from "@/composables/useResponsive"

const utils = useUtils()

const props = defineProps({
    class: String,
    percentage: Number
})

const parsedPercentage = computed(() => {
    return utils.clamp(props.percentage, 0, 100)
})

const barClasses = computed(() => [`progress-${parsedPercentage.value}`])

const containerStyles = computed(() => ({
    height: '4px',
    borderRadius: '0',
    backgroundColor: '#e3e6ea' // lighten($light-3, 2%)
}))

const barStyles = computed(() => ({
    backgroundColor: COLORS.primary,
    width: `${parsedPercentage.value}%`,
    transition: 'none'
}))
</script>

<style scoped>
.progress-bar {
    height: 100%;
}
</style>
