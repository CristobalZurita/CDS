<template>
    <nav class="foxy-navbar"
         :class="shouldExpand ? `foxy-navbar-expanded` : `foxy-navbar-compressed`">
        <div class="foxy-navbar-container container-xxl">
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
import {onMounted, onUnmounted, ref, watch} from "vue"
import Link from "/src/vue/components/generic/Link.vue"
import NavbarBrand from "/src/vue/components/nav/navbar/NavbarBrand.vue"
import NavbarLinks from "/src/vue/components/nav/navbar/NavbarLinks.vue"
import NavbarToggleButton from "/src/vue/components/nav/navbar/NavbarToggleButton.vue"
import {useRoute} from "vue-router"
import {useUtils} from "/src/composables/utils.js"

const route = useRoute()
const utils = useUtils()

const props = defineProps({
    brandLogo: String,
    brandLabel: String,
    brandUrl: String,
    linkList: Array,
    expandable: Boolean
})

const isCollapsed = ref(true)
const shouldExpand = ref(false)

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
