<template>
    <div class="foxy-promo-background">
        <div :class="`foxy-promo-background-overlay-${faded ? `faded` : `default`}`"/>
    </div>
</template>

<script setup>
const props = defineProps({
    faded: Boolean
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

div.foxy-promo-background {
    position: absolute;
    height: calc(100% + 4rem);
    width: 100%;
    z-index: -1;

    background-image: url('/src/assets/header-bg.jpeg');
    background-position: center;
    background-size: cover;
}

div.foxy-promo-background-overlay-default {
    position: relative;
    height: 100%;
    width: 100%;

    background-image: -webkit-gradient(linear, left top, left bottom, from(rgba(30, 30, 30, 0.73)), color-stop(70%, rgba(30, 30, 30, 0.86)), color-stop(80%, rgba(30, 30, 30, 0.99)), to(rgba(30, 30, 30, 1)));
    background-image: linear-gradient(180deg, rgba(30, 30, 30, 0.73) 0%, rgba(30, 30, 30, 0.86) 30%, rgba(30, 30, 30, 0.99) 60%, rgba(30, 30, 30, 1) 100%);
}

div.foxy-promo-background-overlay-faded {
    position: relative;
    height: 100%;
    width: 100%;

    background-image: -webkit-gradient(linear, left top, left bottom, from(rgba(30, 30, 30, 0.83)), color-stop(70%, rgba(30, 30, 30, 0.93)), color-stop(80%, rgba(30, 30, 30, 1)), to(rgba(30, 30, 30, 1)));
    background-image: linear-gradient(180deg, rgba(30, 30, 30, 0.83) 0%, rgba(30, 30, 30, 0.93) 30%, rgba(30, 30, 30, 0.99) 60%, rgba(30, 30, 30, 1) 100%);
}
</style>