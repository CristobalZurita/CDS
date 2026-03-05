<template>
    <div class="foxy-testimonial-item card h-100">
        <!-- Header -->
        <div class="card-header">
            <ImageView :src="props.image || '/images/avatars/default.svg'"
                       :alt="props.title"
                       class="foxy-testimonial-thumbnail"/>

            <h4 class="foxy-testimonial-title ms-3 mt-2"
                v-html="parsedTitle"/>
        </div>

        <div class="card-body text-4">
            <QuotedText :text="parsedQuote"/>
        </div>

        <div class="card-footer">
            <p class="foxy-testimonial-author text-3">
                <span class="text-primary me-2">—</span>

                <span v-html="parsedAuthor"/>

                <span class="opacity-25 mx-1"> · </span>

                <span class="opacity-50"
                      v-html="props.role"/>
            </p>
        </div>
    </div>
</template>

<script setup>
import ImageView from "/src/vue/components/generic/ImageView.vue"
import {computed} from "vue"
import {useUtils} from "/src/composables/utils.js"
import QuotedText from "/src/vue/components/widgets/QuotedText.vue"

const utils = useUtils()

const props = defineProps({
    title: String,
    image: String,
    quote: String,
    role: String,
    author: String
})

const parsedTitle = computed(() => {
    return utils.parseCustomText(props.title)
})

const parsedQuote = computed(() => {
    return utils.parseCustomText(props.quote)
})

const parsedAuthor = computed(() => {
    return utils.parseCustomText(props.author)
})
</script>
