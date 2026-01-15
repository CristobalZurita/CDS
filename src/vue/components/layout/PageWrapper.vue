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

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

div.foxy-page-wrapper {
    @include generate-dynamic-styles-with-hash((
        xxxl: (padding-top:2rem),
        xxl: (padding-top:2.75rem),
        lg: (padding-top:3.5rem),
    ));
}

div.foxy-page-wrapper-no-padding {
    padding-top: 0!important;
}
</style>