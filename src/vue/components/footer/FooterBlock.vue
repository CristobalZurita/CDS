<template>
    <div :style="blockStyles">
        <div class="container-xxl">
            <div v-if="row" class="row" :style="rowStyles">
                <slot/>
            </div>

            <slot v-else/>
        </div>
    </div>
</template>

<script setup>
import { computed } from "vue"
import { useResponsive, COLORS, getResponsiveValue } from "@/composables/useResponsive"

const props = defineProps({
    darken: Boolean,
    row: Boolean,
})

const { windowWidth } = useResponsive()

const blockStyles = computed(() => ({
    minHeight: '40px',
    backgroundColor: props.darken ? COLORS.footerBgHighlight : COLORS.footerBg,
    padding: '2.25rem 0',
    textAlign: 'center'
}))

const rowStyles = computed(() => {
    const padding = getResponsiveValue({
        lg: '2.5rem 0 3rem',
        md: '1.5rem 0',
        sm: '1.5rem 0'
    }, windowWidth.value)

    const textAlign = windowWidth.value >= 992 ? 'left' : 'center'

    return {
        padding,
        rowGap: '2rem',
        alignItems: 'flex-start',
        textAlign
    }
})
</script>
