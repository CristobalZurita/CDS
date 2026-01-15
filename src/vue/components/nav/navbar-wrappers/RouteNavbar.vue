<template>
    <Navbar :brand-logo="logo"
            :brand-label="label"
            brand-url="/"
            :link-list="linkList"
            :expandable="false"/>
</template>

<script setup>
import Navbar from "/src/vue/components/nav/navbar/Navbar.vue"
import {computed} from "vue"
import {useRoute, useRouter} from "vue-router"
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()

const props = defineProps({
    logo: String,
    label: String
})

const authStore = useAuthStore()

const linkList = computed(() => {
    const base = router.getRoutes()
        .map(r => ({
            path: r.path,
            label: r?.props?.default?.label || r.name,
            faIcon: r?.props?.default?.faIcon || 'fa-solid fa-circle',
            isActive: route.path === r.path
        }))
        .filter(r => r.label)

    // If user not authenticated, ensure a visible Login link exists
    if (!authStore.isAuthenticated && !base.find(b => b.path === '/login')) {
        base.push({ path: '/login', label: 'INICIO DE SESIÓN', faIcon: 'fa-solid fa-right-to-bracket', isActive: route.path === '/login' })
    }

    // If authenticated, provide quick access to profile
    if (authStore.isAuthenticated && !base.find(b => b.path === '/profile')) {
        base.push({ path: '/profile', label: 'Perfil', faIcon: 'fa-solid fa-user', isActive: route.path === '/profile' })
    }

    // Link to backend (docs) for quick access during local dev
    if (!base.find(b => String(b.path).includes('127.0.0.1:8000')) ) {
        base.push({ path: 'http://127.0.0.1:8000/docs', label: 'BACK', faIcon: 'fa-solid fa-server', isActive: false })
    }

    return base
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
</style>