<template>
    <article class="foxy-paragraph-article">
        <!-- Heading -->
        <div v-if="props.title"
             class="article-heading">
            <h4 class="mb-2">
                <i v-if="props.faIcon"
                   :class="props.faIcon"
                   class="me-2"/>

                <span v-html="parsedTitle"/>
            </h4>
        </div>

        <!-- Content -->
        <div class="article-content">
            <p v-for="paragraph in description"
               v-html="utils.parseCustomText(paragraph)"
               class="text-3"/>
        </div>
    </article>
</template>

<script setup>
import {computed} from "vue"
import {useUtils} from "/src/composables/utils.js"

const utils = useUtils()

const props = defineProps({
    title: String,
    faIcon: String,
    description: Array
})

const parsedTitle = computed(() => {
    return utils.parseCustomText(props.title)
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

article.foxy-paragraph-article {
    &:not(:last-child) {
        margin-bottom: 2.0rem;
    }
}

div.article-heading {
    color: $dark;
}

p {
    color: $light-7;
    text-align: justify;
    margin-bottom: 1rem;
}
</style>