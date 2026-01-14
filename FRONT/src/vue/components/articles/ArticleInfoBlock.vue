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

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

.article-logo {
    max-width: 320px;  // ajusta este número a gusto (180, 200, 250, etc.)
    max-height: 320px;
    width: 100%;
    height: auto;
    margin: 0 auto;
}


article.foxy-info-block-article {
    display: flex;
    flex-direction: row;
    width: 100%;

    @include media-breakpoint-down(lg) {
        flex-direction: column;
    }
}

div.image-wrapper {
    @include generate-dynamic-styles-with-hash((
        xxxl: (min-width: 30px, margin-right: 4rem),
        xxl:  (min-width: min(33vw, 300px), margin-right: 3.5rem),
        lg:   (min-width: 0, margin-right:0, margin-bottom:2rem, max-width:40vw, max-height:200px)
    ));

    display: flex;
    aspect-ratio: 1/1;
}

div.image-wrapper, div.description-wrapper {
    align-self: center;
    text-align: justify;
}

div.image-wrapper-view {
    width: 100%;
    height: 100%;
    margin: 0 auto;
}

div.description-wrapper {
    width: 100%;
}

p.foxy-article-paragraph {
    font-family: 'Cervo Neue', $font-family-base;
    font-weight: 400;
    line-height: 1.7;
    color: $text-normal;
}

p.foxy-article-paragraph strong {
    font-weight: 700;
}
</style>