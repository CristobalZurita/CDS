<template>
    <div class="foxy-navbar-brand"
         :class="{
             'foxy-navbar-brand-expand': props.expand
         }">

        <!-- Logo -->
        <img :src="props.logo"
             alt="foxy-agency-logo"
             class="img img-fluid foxy-navbar-brand-img"/>

        <!-- Label -->
        <span v-html="parsedLabel"
              class="foxy-navbar-brand-text"/>
    </div>
</template>

<script setup>
import {computed} from "vue"
import {useUtils} from "/src/composables/utils.js"

const utils = useUtils()

const props = defineProps({
    logo: String,
    label: String,
    expand: Boolean
})

const parsedLabel = computed(() => {
    return utils.parseCustomText(props.label)
})
</script>
