<template>
    <div class="foxy-project-info-content">
        <!-- Title -->
        <h1 class="mb-3"
            v-html="parsedTitle"/>

        <!-- Tags Label -->
        <span class="me-2 text-3" v-if="props.tags">
            <i class="pi pi-tags me-1"/>
            {{ strings.get('tags') }}
        </span>

        <!-- Tag List -->
        <div class="d-inline-block" v-if="props.tags">
            <span v-for="tag in props.tags"
                  class="badge bg-primary me-1 text-1">
                {{ tag }}
            </span>
        </div>

        <!-- About -->
        <div class="mt-4" v-if="props.description">
            <h5 class="d-none d-lg-inline-block lead-2">
                <i class="pi pi-lightbulb"/>
                {{ strings.get('about') }}
            </h5>

            <p class="text-4"
               v-html="parsedDescription"/>
        </div>

        <!-- Links -->
        <div class="mt-4" v-if="props.links">
            <h5 class="lead-2">
                <i class="fa-solid fa-external-link me-1 eq-h5"/>
                {{ strings.get('where_to_find') }}
            </h5>

            <p class="text-4"
               v-html="strings.get('project_available_here', [
                  {key: 'title', replacement: parsedTitle}
               ])"
            />

            <SocialLinks v-if="props.links"
                         :items="props.links"
                         size="3"
                         variant="black"/>
        </div>
    </div>
</template>

<script setup>
import {computed} from "vue"
import {useStrings} from "/src/composables/strings.js"
import {useUtils} from "/src/composables/utils.js"
import SocialLinks from "/src/vue/components/widgets/SocialLinks.vue"

const strings = useStrings()
const utils = useUtils()

const props = defineProps({
    title: String,
    tags: Array,
    description: String,
    links: Array,
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
</style>