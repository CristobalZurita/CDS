<template>
    <div class="foxy-section-header">
        <h1 class="foxy-section-header-title" v-html="parsedTitle"/>
        <h5 class="foxy-section-header-subtitle" v-html="parsedSubtitle"/>
    </div>
</template>

<script setup>
import {computed} from "vue"
import {useUtils} from "/src/composables/utils.js"

const utils = useUtils()

const props = defineProps({
    title: String,
    subtitle: String,
    contrast: Boolean
})

const parsedTitle = computed(() => {
    return utils.parseCustomText(props.title, props.contrast)
})

const parsedSubtitle = computed(() => {
    return utils.parseCustomText(props.subtitle)
})
</script>
