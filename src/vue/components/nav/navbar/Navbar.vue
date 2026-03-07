<template>
    <nav :style="navbarStyles">
        <div class="container-xxl" :style="containerStyles">
            <Link :url="brandUrl">
                <NavbarBrand :logo="brandLogo"
                             :label="brandLabel"
                             :expand="shouldExpand"/>
            </Link>

            <NavbarLinks :items="props.linkList"
                         :collapsed="isCollapsed"
                         @link-clicked="_onLinkClicked"/>

            <NavbarToggleButton :collapsed="isCollapsed"
                                @click="_onToggleClicked"/>
        </div>
    </nav>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch, computed } from "vue"
import { useRoute } from "vue-router"
import { useUtils } from "/src/composables/utils.js"
import { useResponsive, COLORS } from "@/composables/useResponsive"
import Link from "/src/vue/components/generic/Link.vue"
import NavbarBrand from "/src/vue/components/nav/navbar/NavbarBrand.vue"
import NavbarLinks from "/src/vue/components/nav/navbar/NavbarLinks.vue"
import NavbarToggleButton from "/src/vue/components/nav/navbar/NavbarToggleButton.vue"

const route = useRoute()
const utils = useUtils()
const { windowWidth } = useResponsive()

const props = defineProps({
    brandLogo: String,
    brandLabel: String,
    brandUrl: String,
    linkList: Array,
    expandable: Boolean
})

const isCollapsed = ref(true)
const shouldExpand = ref(false)

// Navbar styles
const navbarStyles = computed(() => {
    const w = windowWidth.value
    const h = window.innerHeight
    const navbarHeight = 86

    const minHeight = h <= 400 ? `${navbarHeight - 20}px` : `${navbarHeight}px`

    const baseStyles = {
        position: 'fixed',
        top: '0',
        left: '0',
        width: '100vw',
        minHeight,
        zIndex: '10',
        backgroundColor: COLORS.navBg
    }

    if (w >= 992) {
        if (shouldExpand.value) {
            const padding = w >= 1200 ? '15px' : '15px 0'
            return {
                ...baseStyles,
                backgroundColor: 'rgba(0, 0, 0, 0.01)',
                padding,
                transition: '0.3s ease-in-out padding'
            }
        }

        return {
            ...baseStyles,
            transition: '0.3s ease-in-out padding'
        }
    }

    return {
        ...baseStyles,
        transition: 'none'
    }
})

// Container styles
const containerStyles = computed(() => {
    const w = windowWidth.value
    const h = window.innerHeight
    const navbarHeight = 86

    const minHeight = h <= 400 ? `${navbarHeight - 20}px` : `${navbarHeight}px`

    const baseStyles = {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        minHeight,
        height: '100%'
    }

    if (w < 992) {
        return {
            ...baseStyles,
            flexDirection: 'column',
            alignItems: 'start'
        }
    }

    return baseStyles
})

onMounted(() => {
    window.addEventListener('scroll', _onWindowEvent)
    window.addEventListener('resize', _onWindowEvent)
    _onWindowEvent()
})

onUnmounted(() => {
    window.removeEventListener('scroll', _onWindowEvent)
    window.removeEventListener('resize', _onWindowEvent)
})

watch(() => route.path, () => {
    isCollapsed.value = true
})

const _onWindowEvent = () => {
    shouldExpand.value = props.expandable && window.scrollY === 0 && window.innerWidth >= utils.BOOTSTRAP_BREAKPOINTS.lg
}

const _onToggleClicked = () => {
    isCollapsed.value = !isCollapsed.value
}

const _onLinkClicked = () => {
    isCollapsed.value = true
}
</script>
