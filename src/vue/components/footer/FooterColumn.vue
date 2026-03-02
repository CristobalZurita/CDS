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
