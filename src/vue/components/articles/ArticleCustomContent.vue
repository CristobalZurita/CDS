<template>
    <article class="foxy-custom-content-article"
             :class="props.class">
        <slot/>
    </article>
</template>

<script setup>
const props = defineProps({
    class: String
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

article.foxy-custom-content-article {
    @include generate-dynamic-styles-with-hash((
        xxxl: (padding: 2rem 0),
        lg:   (padding: 1rem 0),
        md:   (padding: 0.5rem 0)
    ));

    display: flex;
    flex-direction: column;
    gap: 0;
}
</style>