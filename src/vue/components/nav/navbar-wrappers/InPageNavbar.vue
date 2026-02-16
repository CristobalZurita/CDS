<template>
    <Navbar :brand-logo="logo"
            :brand-label="label"
            brand-url="#"
            :link-list="linkList"
            :expandable="true"/>
</template>

<script setup>
import Navbar from "/src/vue/components/nav/navbar/Navbar.vue"
import {computed, inject, onMounted, onUnmounted, ref, watch} from "vue"
import {useRoute, useRouter} from "vue-router"
import {useLayout} from "/src/composables/layout.js"
import {useAuthStore} from "@/stores/auth"

const route = useRoute()
const router = useRouter()
const layout = useLayout()
const authStore = useAuthStore()

/**
 * @type {{value: SectionInfo[]}}
 */
const currentPageSections = inject("currentPageSections", { value: [] })
const LoaderAnimationStatus = inject("LoaderAnimationStatus", { IDLE: 'IDLE', LOADING: 'LOADING', LEAVING: 'LEAVING' })
const loaderAnimationStatus = inject("loaderAnimationStatus", ref('IDLE'))

const currentSection = ref(null)

const props = defineProps({
    logo: String,
    label: String
})

const linkList = computed(() => {
    const sections = currentPageSections?.value
    const links = (!sections || !sections.length) ? [] : sections.map(section => {
        return {
            path: section.hash,
            label: section.name,
            faIcon: section.faIcon,
            isActive: currentSection.value?.id === section.id
        }
    }).filter(section => section.label && section.path)

    if (route.path !== '/calculadoras') {
        links.push({
            path: '/calculadoras',
            label: 'CALCULADORAS',
            faIcon: 'fa-solid fa-calculator',
            isActive: false
        })
    }

    links.push({
        path: '/login',
        label: 'INICIAR SESIÓN',
        faIcon: 'fa-solid fa-right-to-bracket',
        isActive: route.path === '/login'
    })

    return links
})

onMounted(() => {
    window.addEventListener('scroll', _onWindowEvent)
    window.addEventListener('resize', _onWindowEvent)
    _initSpyScroll()
})

onUnmounted(() => {
    window.removeEventListener('scroll', _onWindowEvent)
    window.removeEventListener('resize', _onWindowEvent)
})

watch(() => loaderAnimationStatus?.value, () => {
    if(loaderAnimationStatus?.value === LoaderAnimationStatus?.LEAVING) {
        _onWindowEvent()
    }
})

const _initSpyScroll = () => {
    setTimeout(() => {
        _onWindowEvent()
        _scrollHashSectionIntoView()
    }, 400)
}

const _scrollHashSectionIntoView = () => {
    const hash = route.hash
    if(!hash)
        return

    const sectionDiv = document.querySelector(hash)
    if(sectionDiv) {
        layout.scrollIntoView(sectionDiv)
    }
}

const _onWindowEvent = () => {
    let lowestOffset = null

    if(window.scrollY < window.innerHeight/4) {
        currentSection.value = null
        return
    }

    const sections = currentPageSections?.value
    for (const section of sections) {
        const sectionDiv = document.querySelector(section.hash)
        if (!sectionDiv) continue

        const offset = Math.abs(sectionDiv.getBoundingClientRect().y)
        if (lowestOffset === null || offset < lowestOffset) {
            lowestOffset = offset
            currentSection.value = section
        }
    }
}
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
</style>
