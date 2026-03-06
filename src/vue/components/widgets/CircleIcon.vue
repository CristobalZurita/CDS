<template>
    <!-- Icon Stack -->
    <span class="fa-stack" :style="iconStackStyles">
        <i class="fas fa-circle fa-stack-2x text-primary"/>
        <i class="fa-stack-1x fa-inverse" :class="props.faIcon"/>
    </span>
</template>

<script setup>
import { computed } from "vue"
import { useResponsive, getResponsiveValue } from "@/composables/useResponsive"

/**
 * @property {String} faIcon
 */
const props = defineProps({
    faIcon: String
})

const { windowWidth } = useResponsive()

const iconStackStyles = computed(() => ({
    fontSize: getResponsiveValue({
        xxxl: '3rem',
        xxl: '2.5rem',
        xl: '2.25rem',
        lg: '2rem',
        md: '1.5rem',
        sm: '1.25rem'
    }, windowWidth.value)
}))
</script>
