<template>
    <router-link v-if="isRouterLink"
                 :to="url">
        <slot/>
    </router-link>

    <button v-else-if="isHashLink"
            class="btn-link-wrapper"
            @click="_onHashLinkClicked">
        <slot/>
    </button>

    <a v-else-if="isExternalLink"
       class="btn-link-wrapper"
       :href="url"
       target="_blank">
        <slot/>
    </a>
</template>

<script setup>
import {computed} from "vue"
import {useLayout} from "/src/composables/layout.js"
import {useRoute, useRouter} from "vue-router"

const props = defineProps({
    url: String
})

const layout = useLayout()
const route = useRoute()
const router = useRouter()

const isRouterLink = computed(() => {
    return String(props.url).charAt(0) === "/"
})

const isHashLink = computed(() => {
    return String(props.url).charAt(0) === "#"
})

const isExternalLink = computed(() => {
    return String(props.url).includes('http')
})

const _onHashLinkClicked = () => {
    if(props.url === "#") {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        })
        window.location.hash = ''
        return
    }

    window.location.hash = props.url
    const sectionDiv = document.querySelector(props.url)
    if(sectionDiv) {
        layout.scrollIntoView(sectionDiv)
        return
    }

    // Fallback: if current route has no matching section, navigate to home hash.
    if(route.path !== "/") {
        router.push({ path: "/", hash: props.url })
    }
}
</script>
