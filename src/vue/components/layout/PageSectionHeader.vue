<template>
    <div :style="headerStyles">
        <h1 :style="titleStyles" v-html="parsedTitle"/>
        <h5 :style="subtitleStyles" v-html="parsedSubtitle"/>
    </div>
</template>

<script setup>
import { computed } from "vue"
import { useUtils } from "@/composables/utils.js"
import { useResponsive, COLORS, getResponsiveValue } from "@/composables/useResponsive"

const utils = useUtils()
const { windowWidth } = useResponsive()

const props = defineProps({
    title: String,
    subtitle: String,
    contrast: Boolean
})

const parsedTitle = computed(() => {
    return utils.parseCustomText(props.title, props.contrast)
})

const parsedSubtitle = computed(() => {
    return utils.parseCustomText(props.subtitle)
})

// Margin-bottom responsive
const headerMarginBottom = computed(() => {
    return getResponsiveValue({
        xxxl: '4rem',
        xxl: '3rem',
        lg: '3rem',
        md: '2.75rem',
        sm: '2.5rem'
    }, windowWidth.value)
})

const headerStyles = computed(() => ({
    marginBottom: headerMarginBottom.value,
    textAlign: 'center'
}))

const titleStyles = computed(() => ({
    textTransform: 'uppercase',
    color: 'inherit',
    fontFamily: 'inherit',
    fontWeight: '800',
    letterSpacing: '0.02em',
    fontSize: 'inherit'
}))

const subtitleStyles = computed(() => ({
    fontFamily: 'inherit',
    color: COLORS.textMuted,
    fontWeight: '500',
    letterSpacing: '0.02em',
    marginTop: '1rem',
    fontSize: 'inherit'
}))
</script>
