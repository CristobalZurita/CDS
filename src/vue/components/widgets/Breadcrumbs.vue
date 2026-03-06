<template>
    <nav v-if="breadcrumbItems" class="breadcrumbs">
        <ul class="breadcrumbs-list" :style="listStyles">
            <!-- Breadcrumb Item -->
            <li v-for="(route, index) in breadcrumbItems"
                class="breadcrumb-item text-4">
                <!-- First Item -->
                <router-link v-if="index === 0 && route.path === '/'" :to="route.path">
                    <i class="me-1 fa-solid fa-home"/>
                </router-link>

                <!-- Other Items -->
                <router-link v-else-if="index <= breadcrumbItems.length - 1" :to="route.path">
                    {{ route.props?.default?.label }}
                </router-link>
            </li>

            <!-- Current Item -->
            <li class="breadcrumb-item text-4">
                {{ currentRouteLabel }}
            </li>
        </ul>
    </nav>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router"
import { computed } from "vue"
import { useResponsive } from "@/composables/useResponsive"

const route = useRoute()
const router = useRouter()
const routes = router.getRoutes()
const { windowWidth } = useResponsive()

const currentRoute = computed(() => {
    return routes.find(r => r.name === route.name)
})

const listStyles = computed(() => ({
    listStyle: 'none',
    display: 'flex',
    alignItems: 'center',
    padding: '0',
    justifyContent: windowWidth.value <= 768 ? 'center' : 'flex-start'
}))

const currentRouteLabel = computed(() => {
    return currentRoute.value?.props?.default?.label
})

const breadcrumbItems = computed(() => {
    const breadcrumbs = currentRoute.value?.props?.default?.breadcrumbs
    if(!breadcrumbs)
        return []

    return breadcrumbs.map((url) => {
        const route = routes.find(r => r.path === url)
        if(route) {
            return route
        }
    }).filter(item => item !== undefined && item !== null)
})
</script>

<style scoped>
.breadcrumb-item {
    margin-right: 0.3rem;
    color: #6c757d;
}

.breadcrumb-item:not(:last-child)::after {
    content: "›";
    color: #6c757d;
    margin-left: 0.2rem;
}
</style>
