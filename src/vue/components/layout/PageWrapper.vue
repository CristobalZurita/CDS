<template>
    <div class="foxy-page-wrapper"
         :class="noPadding ? `foxy-page-wrapper-no-padding` : ``"
         :id="props.id">
        <div :class="`foxy-page-inner ${props.readable ? 'readable' : ''}`">
            <component v-for="sectionInfo in sections"
                       :is="sectionInfo.component"
                       :id="sectionInfo.id"/>
        </div>
    </div>
</template>

<script setup>
import SectionInfo from "/src/models/SectionInfo.js"
import {inject, onBeforeMount, ref} from "vue"

const currentPageSections = inject("currentPageSections")

const props = defineProps({
    id: String,
    noPadding: Boolean,
    readable: Boolean,
    sections: {
        type: Array,
        validator(value) { return value.every(item => item instanceof SectionInfo) },
        required: true
    }
})

onBeforeMount(() => {
    currentPageSections.value = props.sections
})
</script>
