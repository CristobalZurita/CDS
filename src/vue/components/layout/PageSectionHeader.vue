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

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

div.foxy-section-header {
    @include generate-dynamic-styles-with-hash((
        xxxl: (margin-bottom: 4rem),
        xxl:  (margin-bottom: 3rem),
        lg:   (margin-bottom: 3rem),
        md:   (margin-bottom: 2.75rem),
        sm:   (margin-bottom: 2.5rem),
    ));

    text-align: center;
    
}
:deep(.foxy-section-header-title span) {
  font-size: inherit;
}

h1 {
    text-transform: uppercase;
    color: inherit;
    font-family: inherit;
    font-weight: 800;
    letter-spacing: 0.02em;
    font-size: inherit;
}



h5 {
    font-family: inherit;
    color: $text-muted;
    font-weight: 500;
    letter-spacing: 0.02em;
    margin-top: 1rem;   // SUBE el texto
    font-size: inherit;
}
</style>
