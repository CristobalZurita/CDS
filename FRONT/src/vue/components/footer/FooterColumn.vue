<template>
    <div class="foxy-footer-col col-12 col-lg-4">
        <!-- Column Title -->
        <h5 class="foxy-footer-col-title">
            <i v-if="props.faIcon"
               :class="props.faIcon"/>

            <span>{{props.title}}</span>
        </h5>

        <!-- Description -->
        <div v-if="props.description.length > 0"
             class="foxy-footer-col-item">
            <div class="foxy-footer-col-description">
                <p v-for="descriptionItem in props.description" class="text-2 m-0" v-html="descriptionItem"/>
            </div>
        </div>

        <!-- Circle Links -->
        <div v-if="props.links.length > 0 && props.displayLinksAsButtons"
             class="foxy-footer-col-item mt-3">
            <SocialLinks :items="props.links"
                         variant="dark"
                         size="3"/>
        </div>

        <!-- Inline Links -->
        <div v-if="props.links.length > 0 && !props.displayLinksAsButtons"
             class="foxy-footer-col-item mt-2 mt-lg-1">
            <InlineLinkList :items="props.links"/>
        </div>
    </div>
</template>

<script setup>
import SocialLinks from "/src/vue/components/widgets/SocialLinks.vue"
import InlineLinkList from "/src/vue/components/widgets/InlineLinkList.vue"

const props = defineProps(({
    title: String,
    faIcon: String,
    description: Array,
    links: Array,
    displayLinksAsButtons: Boolean
}))
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

p, span {
    color: #eaeaea; /* increase contrast for footer text */
    font-size: 1.02rem;
}

div.foxy-footer-col {
    @include media-breakpoint-down(lg) {
        padding-top: 1.5rem;
        padding-bottom: 2rem;

        &:first-child {
            padding-top: 0;
        }

        &:not(:first-child) {
            border-top: 1px solid lighten($dark, 3%);
        }

        &:last-child {
            padding-bottom: 0;
        }
    }
}

h5.foxy-footer-col-title {
    i, span {
        color: $light-1;
        text-transform: uppercase;
    }
}

div.foxy-footer-col-item {
    display: flex;
    align-items: center;
    justify-content: center;

    @include generate-dynamic-styles-with-hash((
        xxxl: (padding-top:0.5rem),
        lg: (padding-top:0.3rem),
    ));

    margin: 0 auto;
    max-width: 380px;
}

div.foxy-footer-col-description {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: start;
}
</style>