<template>
    <nav v-if="breadcrumbItems" class="breadcrumbs">
        <ul class="breadcrumbs-link-list">
            <!-- Breadcrumb Item -->
            <li v-for="(route, index) in breadcrumbItems"
                class="breadcrumb-link-item text-4">
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
            <li class="breadcrumb-link-item text-4">
                {{ currentRouteLabel }}
            </li>
        </ul>
    </nav>
</template>

<script setup>
import {useRoute, useRouter} from "vue-router"
import {computed} from "vue"

const route = useRoute()
const router = useRouter()
const routes = router.getRoutes()

const currentRoute = computed(() => {
    return routes.find(r => r.name === route.name)
})

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

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

ul.breadcrumbs-link-list {
    list-style: none;
    display: flex;
    align-items: center;
    padding: 0;

    @include media-breakpoint-down(md) {
        justify-content: center;
    }
}

li.breadcrumb-link-item {
    margin-right: 0.3rem;

    color: $light-6;
    &:not(:last-child)::after {
        content: "›";
        color: $light-6;
        margin-left: 0.2rem;
    }
}
</style>