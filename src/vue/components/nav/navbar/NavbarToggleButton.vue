<template>
    <button :style="buttonStyles"
            type="button">
        <i :class="icon"
           class="ms-1 me-1"/>
    </button>
</template>

<script setup>
import { computed } from "vue"
import { useResponsive, COLORS, LAYOUT } from "@/composables/useResponsive"

const props = defineProps({
    collapsed: Boolean
})

const { windowWidth } = useResponsive()

const icon = computed(() => {
    return props.collapsed ?
        `fas fa-bars` :
        `fas fa-minimize`
})

const buttonStyles = computed(() => {
    const buttonSize = '40px'
    const navbarHeight = 86 // px

    // Hide on desktop (lg and up)
    if (windowWidth.value >= 992) {
        return { display: 'none' }
    }

    // Adjust top position for very short screens
    const topOffset = windowWidth.value <= 400
        ? `calc(${navbarHeight}px / 2 - ${buttonSize} / 2 - 5px)`
        : `calc(${navbarHeight}px / 2 - ${buttonSize} / 2)`

    const baseStyles = {
        position: 'absolute',
        top: topOffset,
        right: '25px',
        width: buttonSize,
        height: buttonSize,
        fontSize: '0.75rem',
        fontFamily: "'Steelfish', 'Cervo Neue', 'Oswald', serif",
        fontWeight: '700',
        borderRadius: '10px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        outline: 'none',
        boxShadow: 'none'
    }

    if (props.collapsed) {
        return {
            ...baseStyles,
            backgroundColor: COLORS.navBg,
            border: `2px solid ${COLORS.navBgLight}`,
            color: COLORS.light4
        }
    }

    return {
        ...baseStyles,
        backgroundColor: COLORS.navBgLight,
        border: `2px solid ${COLORS.navBgLighter}`,
        color: COLORS.white
    }
})
</script>
