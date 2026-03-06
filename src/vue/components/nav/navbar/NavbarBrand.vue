<template>
    <div :style="brandStyles">
        <!-- Logo -->
        <img :src="props.logo"
             alt="foxy-agency-logo"
             class="img img-fluid"
             :style="imgStyles"/>

        <!-- Label -->
        <span v-html="parsedLabel"/>
    </div>
</template>

<script setup>
import { computed } from "vue"
import { useUtils } from "/src/composables/utils.js"
import { useResponsive, COLORS, getResponsiveValue } from "@/composables/useResponsive"

const utils = useUtils()
const { windowWidth } = useResponsive()

const props = defineProps({
    logo: String,
    label: String,
    expand: Boolean
})

const parsedLabel = computed(() => {
    return utils.parseCustomText(props.label)
})

// Brand wrapper styles
const brandStyles = computed(() => {
    const w = windowWidth.value
    const h = window.innerHeight

    // Font size responsive
    let fontSize
    if (props.expand) {
        fontSize = w >= 1200 ? '1.5rem' : '1.45rem'
    } else {
        fontSize = getResponsiveValue({
            xxxl: '1.4rem',
            lg: '1.25rem',
            md: '1.25rem',
            sm: '1.25rem'
        }, w)

        // Very short screens
        if (h <= 400) {
            fontSize = '1.2rem'
        }
    }

    const baseStyles = {
        display: 'inline-flex',
        alignItems: 'center',
        whiteSpace: 'nowrap',
        textTransform: 'uppercase',
        fontFamily: 'inherit',
        fontWeight: '700',
        color: COLORS.white,
        marginTop: '5px',
        marginLeft: '0',
        padding: '5px 0 5px',
        fontSize
    }

    if (w >= 992) {
        return {
            ...baseStyles,
            transition: 'font-size 0.3s ease-in-out'
        }
    }

    return {
        ...baseStyles,
        paddingTop: '8px',
        transition: 'none'
    }
})

// Image styles
const imgStyles = computed(() => {
    const w = windowWidth.value
    const h = window.innerHeight

    let imgSize
    if (props.expand) {
        imgSize = w >= 1200 ? { width: '3.4rem', height: '3.4rem' } : { width: '3.2rem', height: '3.2rem' }
    } else {
        const size = getResponsiveValue({
            xxxl: '3.4rem',
            lg: '3rem',
            md: '3rem',
            sm: '3rem'
        }, w)
        imgSize = { width: size, height: size }

        // Very short screens
        if (h <= 400) {
            imgSize = { width: '2.5rem', height: '2.5rem' }
        }
    }

    const baseStyles = {
        position: 'relative',
        top: '-0.1rem',
        marginRight: '0.5rem',
        ...imgSize
    }

    if (w >= 992) {
        return {
            ...baseStyles,
            transition: 'height 0.3s ease-in-out, width 0.3s ease-in-out'
        }
    }

    return {
        ...baseStyles,
        transition: 'none'
    }
})
</script>
