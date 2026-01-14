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

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

div.foxy-navbar-brand {
    @include generate-dynamic-styles-with-hash((
        xxxl: (font-size: 1.4rem),
        lg:   (font-size: 1.25rem)
    ));

    img.foxy-navbar-brand-img {
        height: 3rem;
        width: 3rem;
    }

    display: inline-flex;
    align-items: center;
    text-transform: uppercase;
    font-family: $headings-font-family;
    font-weight: $headings-font-weight;
    color: $text-normal-contrast;
    margin-top: 5px;
    transition: font-size 0.3s ease-in-out;
    padding: 5px 0 5px;

    @include media-breakpoint-down(lg) {
        padding-top: 8px;
        transition: none;
    }

    @media (max-height: 400px) {
        font-size: 1.2rem;
    }
}

img.foxy-navbar-brand-img {
    @include generate-dynamic-styles-with-hash((
        xxxl: (height: 3.4rem, width: 3.4rem),
        lg:   (height: 3rem, width: 3rem)
    ));

    position: relative;
    top: -0.1rem;
    margin-right: 0.5rem;
    transition: height 0.3s ease-in-out, width 0.3s ease-in-out;
    @include media-breakpoint-down(lg) {
        transition: none;
    }

    @media (max-height: 400px) {
        height: 2.5rem!important;
        width: 2.5rem!important;
    }
}

div.foxy-navbar-brand-expand {
    font-size: 1.5rem;
    img.foxy-navbar-brand-img {
        width: 3.4rem;
        height: 3.4rem;
    }

    @include media-breakpoint-down(xl) {
        font-size: 1.45rem;
        img.foxy-navbar-brand-img {
            width: 3.2rem;
            height: 3.2rem;
        }
    }
}
</style>