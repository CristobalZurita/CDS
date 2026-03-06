import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

// Breakpoints existentes (de _variables.scss)
export const BREAKPOINTS = {
    sm: 576,
    md: 768,
    lg: 992,
    xl: 1200,
    xxl: 1400,
    xxxl: 1600
}

// Constantes de layout (de _variables.scss)
export const LAYOUT = {
    navbarHeight: '86px'
}

// Colores existentes (de _variables.scss)
export const COLORS = {
    light: '#d3d0c3',
    primary: '#ec6b00',
    primaryLight: '#f9d4b3',
    primaryLighter: '#f89d4d',
    primaryHover: '#f07519',
    primaryHoverLight: '#faa967',
    dark: '#3e3c38',
    darkLight: '#565450',
    darkLighter: '#45423e',
    white: '#ffffff',
    light1: '#f8f9fa',
    light3: '#dee2e6',
    light4: '#ced4da',
    light6: '#6c757d',
    lightShade5: '#adb5bd',
    textMuted: '#5a5652',
    gray240: '#eaeaea',
    footerBg: '#3e3c38',
    footerBgHighlight: '#3a3834',
    navBg: '#3e3c38',
    navBgLight: '#48453f',
    navBgLighter: '#524e46'
}

/**
 * Composable para responsive con window resize
 */
export function useResponsive() {
    const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1920)

    const updateWidth = () => {
        windowWidth.value = window.innerWidth
    }

    onMounted(() => {
        if (typeof window !== 'undefined') {
            window.addEventListener('resize', updateWidth)
        }
    })

    onBeforeUnmount(() => {
        if (typeof window !== 'undefined') {
            window.removeEventListener('resize', updateWidth)
        }
    })

    const isMobile = computed(() => windowWidth.value < BREAKPOINTS.md)
    const isTablet = computed(() => windowWidth.value >= BREAKPOINTS.md && windowWidth.value < BREAKPOINTS.lg)
    const isDesktop = computed(() => windowWidth.value >= BREAKPOINTS.lg)

    return {
        windowWidth,
        isMobile,
        isTablet,
        isDesktop,
        BREAKPOINTS
    }
}

/**
 * Helper para valores responsive basados en breakpoints
 * @param {Object} values - { xxxl: valor, xxl: valor, lg: valor, md: valor, sm: valor }
 * @param {Number} width - Window width actual
 */
export function getResponsiveValue(values, width) {
    if (width >= BREAKPOINTS.xxxl && values.xxxl !== undefined) return values.xxxl
    if (width >= BREAKPOINTS.xxl && values.xxl !== undefined) return values.xxl
    if (width >= BREAKPOINTS.xl && values.xl !== undefined) return values.xl
    if (width >= BREAKPOINTS.lg && values.lg !== undefined) return values.lg
    if (width >= BREAKPOINTS.md && values.md !== undefined) return values.md
    return values.sm !== undefined ? values.sm : values.md || values.lg
}
