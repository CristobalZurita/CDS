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
                <p v-for="descriptionItem in props.description" class="m-0" v-html="descriptionItem"/>
            </div>
        </div>

        <!-- Circle Links -->
        <div v-if="props.links.length > 0 && props.displayLinksAsButtons"
             class="foxy-footer-col-item mt-3">
            <SocialLinks :items="props.links"
                         variant="dark"
                         size="4"/>
        </div>

        <!-- Inline Links -->
        <div v-if="props.links.length > 0 && !props.displayLinksAsButtons"
             class="foxy-footer-col-item mt-2 mt-lg-1">
            <ul class="footer-inline-links">
                <li v-for="(link, index) in props.links" :key="index" class="footer-inline-link-item">
                    <a v-if="link.href && !link.href.startsWith('/')"
                       :href="link.href"
                       target="_blank"
                       rel="noopener noreferrer"
                       class="footer-inline-link">
                        {{ link.label }}
                    </a>
                    <router-link v-else
                                 :to="link.href"
                                 class="footer-inline-link">
                        {{ link.label }}
                    </router-link>
                </li>
            </ul>
        </div>
    </div>
</template>

<script setup>
import SocialLinks from "/src/vue/components/widgets/SocialLinks.vue"
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
    color: $color-gray-240-legacy; /* increase contrast for footer text */
    font-size: 1.25rem;
    line-height: 1.7;
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

    @include media-breakpoint-up(lg) {
        text-align: left;
    }
}

h5.foxy-footer-col-title {
    i, span {
        color: $light-1;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.08em;
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
    max-width: 520px;

    @include media-breakpoint-up(lg) {
        align-items: flex-start;
        justify-content: flex-start;
        margin: 0;
        max-width: 620px;
    }
}

div.foxy-footer-col-description {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: start;

    @include media-breakpoint-up(lg) {
        align-items: flex-start;
    }
}

ul.footer-inline-links {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    align-items: center;
    gap: 1.1rem;
    white-space: normal;
}

li.footer-inline-link-item {
    display: inline-flex;
    align-items: center;
}

li.footer-inline-link-item:not(:last-child)::after {
    content: "·";
    color: $color-gray-240-legacy;
    margin-left: 0.6rem;
}

.footer-inline-link {
    text-decoration: none;
    color: $color-gray-240-legacy;
    font-weight: 700;
    white-space: nowrap;
}

.footer-inline-link:hover {
    color: lighten($primary, 15%);
}
</style>
