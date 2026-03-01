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

<style lang="scss" scoped>
@use "@/scss/_theming.scss" as *;

div.progress {
    height: 4px;
    border-radius: 0;
    background-color: lighten($light-3, 2%);
}

div.progress-bar {
    background-color: $primary;
    -webkit-transition: none;
    -moz-transition: none;
    -ms-transition: none;
    -o-transition: none;
    transition: none;

    @for $i from 0 through 100 {
        &.progress-#{$i} {
            width: #{$i}%;
        }
    }
}
</style>
