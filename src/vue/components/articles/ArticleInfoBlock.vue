<template>
    <article class="foxy-info-block-article">
        <div class="image-wrapper">
            <ImageView :src="image"
                       alt="Logo"
                        class="article-logo"/>
        </div>

        <div class="description-wrapper">
            <p v-for="paragraph in parsedParagraphs"
               class="text-4 foxy-article-paragraph"
               v-html="paragraph"/>
        </div>
    </article>
</template>

<script setup>
import ImageView from "/src/vue/components/generic/ImageView.vue"
import {computed} from "vue"

const props = defineProps({
    image: String,
    paragraphs: Array
})

const parsedParagraphs = computed(() => {
    return props.paragraphs || []
})
</script>
