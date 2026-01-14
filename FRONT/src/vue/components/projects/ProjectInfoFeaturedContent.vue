<template>
    <div class="foxy-project-info-featured-content">
        <h4 class="title mb-2 text-light-5">
            <i class="fa-solid fa-fire me-2"/>
            {{ strings.get('latest_release') }}
        </h4>

        <h1 class="project-title display-1 text-white text-uppercase"
            v-html="parsedTitle"/>

        <p class="description eq-h6 text-light-5 mt-4 mb-4"
           v-html="parsedDescription"/>

        <SocialLinks v-if="props.links"
                     :items="props.links"
                     size="4"
                     variant="black"
                     class="pt-xl-3"/>
    </div>
</template>

<script setup>
import {useStrings} from "/src/composables/strings.js"
import {computed} from "vue"
import {useUtils} from "/src/composables/utils.js"
import SocialLinks from "/src/vue/components/widgets/SocialLinks.vue"

const strings = useStrings()
const utils = useUtils()

const props = defineProps({
    title: String,
    description: String,
    links: Array
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