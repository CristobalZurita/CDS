<template>
    <div class="foxy-quote-item px-0 px-lg-3 px-xl-4 mx-auto">
        <!-- Quote Balloon -->
        <div v-if="quote"
             class="foxy-quote-balloon">
            <div class="triangle"/>

            <QuotedText class="text-muted text-3 mx-3"
                        :text="parsedQuote"/>
        </div>

        <!-- Avatar -->
        <ImageView :src="props.image"
                   :alt="props.title"
                   class="foxy-quote-avatar"/>

        <!-- Texts And Links -->
        <div class="foxy-quote-about">
            <h4 class="my-3 mt-2 mt-xxl-3 mb-1"
                v-html="parsedTitle"/>

            <p class="text-muted text-4 mb-2 pb-1"
               v-html="role"/>

            <SocialLinks v-if="props.links"
                         :items="props.links"
                         size="2"
                         variant="black"/>
        </div>
    </div>
</template>

<script setup>
import {computed} from "vue"
import {useUtils} from "/src/composables/utils.js"
import ImageView from "/src/vue/components/generic/ImageView.vue"
import SocialLinks from "/src/vue/components/widgets/SocialLinks.vue"
import QuotedText from "/src/vue/components/widgets/QuotedText.vue"

const utils = useUtils()

const props = defineProps({
    title: String,
    role: String,
    image: String,
    quote: String,
    links: Array
})

const parsedTitle = computed(() => {
    return utils.parseCustomText(props.title)
})

const parsedQuote = computed(() => {
    return utils.parseCustomText(props.quote)
})
</script>
