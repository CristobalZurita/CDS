<template>
    <article class="foxy-features-article row">
        <slot/>
    </article>
</template>

<script setup>
</script>

<style lang="scss" scoped>
@use "@/scss/_theming.scss" as *;

article.foxy-features-article {
    text-align: center;
    row-gap: 30px;
    @include media-breakpoint-down(lg) {
        row-gap: 30px;
    }
}
</style>