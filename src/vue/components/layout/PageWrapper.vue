<template>
    <div :style="wrapperStyles"
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
import { inject, onBeforeMount, onUnmounted, computed } from "vue"
import { useResponsive, getResponsiveValue } from "@/composables/useResponsive"

const currentPageSections = inject("currentPageSections")
const { windowWidth } = useResponsive()

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

// Padding-top responsive
const wrapperPaddingTop = computed(() => {
    if (props.noPadding) return '0'

    return getResponsiveValue({
        xxxl: '2rem',
        xxl: '2.75rem',
        lg: '3.5rem',
        md: '3.5rem',
        sm: '3.5rem'
    }, windowWidth.value)
})

const wrapperStyles = computed(() => ({
    paddingTop: wrapperPaddingTop.value
}))

onBeforeMount(() => {
    if (currentPageSections) {
        currentPageSections.value = props.sections
    }
})

onUnmounted(() => {
    // Avoid leaking in-page section links into routes that do not define sections.
    if (currentPageSections) {
        currentPageSections.value = []
    }
})
</script>
