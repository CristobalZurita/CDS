<template>
    <div class="foxy-item-feature col-12 col-md-6 col-lg-4">
        <div class="foxy-item-feature-content mb-lg-4">
            <div class="foxy-item-feature-icon-wrapper">
                <CircleIcon :fa-icon="faIcon"/>
            </div>

            <div class="foxy-item-feature-content-wrapper">
                <h5 v-html="parsedTitle" class="mb-1 mb-sm-2 foxy-feature-title"/>

                <p class="text-muted text-4 mb-0 foxy-feature-description"
                   v-html="parsedDescription"/>
            </div>
        </div>
    </div>
</template>

<script setup>
import {computed} from "vue"
import {useUtils} from "/src/composables/utils.js"
import CircleIcon from "/src/vue/components/widgets/CircleIcon.vue"

const utils = useUtils()

const props = defineProps({
    title: String,
    faIcon:String,
    description: String
})

const parsedTitle = computed(() => {
    return utils.parseCustomText(props.title)
})

const parsedDescription = computed(() => {
    return utils.parseCustomText(props.description)
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

div.foxy-item-feature-content {
    @include generate-dynamic-styles-with-hash((
        xxxl: (flex-direction: column, padding: 0 1rem),
        lg:   (flex-direction: row, text-align:left, padding: 0 0.5rem),
        md:   (padding: 0)
    ));

    display: flex;
}

div.foxy-item-feature-content-wrapper {
    @include generate-dynamic-styles-with-hash((
        xxxl: (margin-top: 1rem),
        lg:   (margin-top: 0, margin-left: 1rem),
        md:   (margin-left: 0.75rem)
    ));
}

h5.foxy-feature-title {
    font-family: 'Cervo Neue', $headings-font-family;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: $dark;
}

p.foxy-feature-description {
    font-family: 'Cervo Neue', $font-family-base;
    font-weight: 400;
    line-height: 1.6;
}
</style>