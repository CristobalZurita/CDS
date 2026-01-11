<template>
    <article class="foxy-features-article row">
        <slot/>
    </article>
</template>

<script setup>
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

article.foxy-features-article {
    text-align: center;
    row-gap: 30px;
    @include media-breakpoint-down(lg) {
        row-gap: 30px;
    }
}
</style>