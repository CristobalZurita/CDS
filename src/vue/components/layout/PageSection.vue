<template>
    <section
        ref="sectionRef"
        :id="id"
        :data-zone="id"
        :style="sectionStyles"
        :class="animationClass">

        <BackgroundPromo v-if="variant === 'promo'" :faded="true"/>

        <div :style="containerStyles">
            <header v-if="$slots.header">
                <slot name="header" />
            </header>

            <div :style="contentStyles">
                <slot />
            </div>

            <footer v-if="$slots.footer">
                <slot name="footer" />
            </footer>
        </div>
    </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue"
import { track } from "@/analytics"
import { AnalyticsEvents } from "@/analytics/events"
import BackgroundPromo from "./BackgroundPromo.vue"
import { useResponsive, COLORS, getResponsiveValue } from "@/composables/useResponsive"

const props = defineProps({
    id: String,
    variant: {
        type: String,
        default: 'default',
        validator: (v) => ['default', 'primary', 'dark', 'promo'].includes(v)
    },
    name: String,
    faIcon: String
})

const { windowWidth } = useResponsive()

// Padding responsive
const sectionPadding = computed(() => {
    return getResponsiveValue({
        xxxl: '5rem 0 5.5rem',
        xxl: '4rem 0 4.5rem',
        lg: '3rem 0 3.5rem',
        md: '3rem 0 3.5rem',
        sm: '2.5rem 0 3rem'
    }, windowWidth.value)
})

// Container padding responsive
const containerPadding = computed(() => {
    const w = windowWidth.value
    if (w >= 1600) return '0'
    if (w >= 1400) return '0 4rem'
    if (w >= 1200) return '0 2rem'
    if (w >= 992) return '0 2rem'
    if (w >= 768) return '0 2.25rem'
    if (w <= 380) return '0 1.35rem'
    return '0 1.75rem'
})

// Estilos de sección
const sectionStyles = computed(() => {
    const base = {
        position: 'relative',
        padding: sectionPadding.value,
        opacity: animationClass.value === 'is-visible' ? 1 : 0,
        transform: animationClass.value === 'is-visible' ? 'translateY(0)' : 'translateY(16px)',
        transition: 'opacity 0.6s ease, transform 0.6s ease'
    }

    const variants = {
        default: { backgroundColor: COLORS.light },
        primary: { backgroundColor: COLORS.primaryLight },
        dark: { backgroundColor: COLORS.darkLight, color: COLORS.white },
        promo: { backgroundColor: 'transparent' }
    }

    return { ...base, ...variants[props.variant] }
})

const containerStyles = computed(() => ({
    padding: containerPadding.value
}))

const contentStyles = computed(() => ({
    maxWidth: '1200px',
    width: '100%',
    marginLeft: 'auto',
    marginRight: 'auto'
}))

// Animation
const sectionRef = ref(null)
const animationClass = ref('')
let observer = null

onMounted(() => {
    if (!sectionRef.value) return
    observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                animationClass.value = 'is-visible'
                track(AnalyticsEvents.SECTION_FOCUS, null, {
                    page: window.location.pathname,
                    section: props.id || 'unknown'
                })
            }
        })
    }, { threshold: 0.35 })
    observer.observe(sectionRef.value)
})

onBeforeUnmount(() => {
    if (observer && sectionRef.value) {
        observer.unobserve(sectionRef.value)
    }
    observer = null
})
</script>

<style scoped>
/* Solo para selector descendiente h5 en dark variant */
section[data-variant="dark"] :deep(h5) {
    color: #adb5bd;
}
</style>
