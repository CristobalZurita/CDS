<template>
    <p class="text-1"
       :style="copyrightStyles"
       v-html="formattedCopyright"/>
</template>

<script setup>
import { computed } from "vue"
import { useStrings } from "/src/composables/strings.js"

const strings = useStrings()

const props = defineProps({
    holder: String,
    url: String,
    license: String,
})

const copyrightStyles = computed(() => ({
    color: '#e6e6e6',
    padding: '0',
    margin: '0',
    fontSize: '0.98rem'
}))

const formattedCopyright = computed(() => {
    return strings.getCopyrightMessage(
        new Date().getFullYear().toString(),
        props.holder,
        props.url,
        props.license
    )
})
</script>
