<template>
    <div class="navigation">
        <!-- In-page Navigation -->
        <InPageNavbar v-if="shouldDisplayInPageNavBar && !isAdminRoute"
                      :logo="logo"
                      :label="label"/>

        <!-- Router Navigation -->
        <RouteNavbar v-else
                     :logo="logo"
                     :label="label"/>
    </div>
</template>

<script setup>
import {useRoute, useRouter} from "vue-router"
import {computed} from "vue"
import {useLayout} from "/src/composables/layout.js"
import RouteNavbar from "/src/vue/components/nav/navbar-wrappers/RouteNavbar.vue"
import InPageNavbar from "/src/vue/components/nav/navbar-wrappers/InPageNavbar.vue"

const route = useRoute()
const router = useRouter()
const _layout = useLayout()

const _props = defineProps({
    logo: String,
    label: String
})

const shouldDisplayInPageNavBar = computed(() => {
    const routeInfo = router.getRoutes().find(r => r.name === route.name)
    if(!routeInfo || !routeInfo.props || !routeInfo.props.default)
        return true

    return routeInfo.props.default['inPageNavbar']
})

const isAdminRoute = computed(() => route.path.startsWith('/admin'))
</script>
