<template>
    <div class="foxy-project-info">
        <!-- Logo Wrapper -->
        <div class="foxy-project-info-logo-wrapper"
             :class="shrinkImage ? `foxy-project-info-logo-wrapper-shrink` : ``">
            <ImageView :src="props.image"
                       alt="Logo"
                       :spinner-enabled="true"/>
        </div>

        <div class="foxy-project-info-content">
            <slot/>
        </div>
    </div>
</template>

<script setup>
import ImageView from "/src/vue/components/generic/ImageView.vue"

const props = defineProps({
    image: String,
    shrinkImage: Boolean
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

div.foxy-project-info {
    @include generate-dynamic-styles-with-hash((
        xxxl: (flex-direction: row, width: 100%, padding: 2rem),
        lg:   (flex-direction: column, padding: 1rem, align-items: center),
        md:   (padding: 0.5rem)
    ));

    display: flex;
}

div.foxy-project-info-logo-wrapper {
    @include generate-dynamic-styles-with-hash((
        xxxl: (height: 320px, min-width: 320px, margin-right: 6rem),
        xl:   (height: 300px, min-width: 300px, margin-right: 4rem),
        lg:   (height: min(230px, 35vw), min-width: 0, width: min(230px, 35vw), margin-right:0, margin-bottom: 1rem),
        md:   (width: min(200px, 35vw), height: min(200px, 35vw)),
        sm:   (width: min(170px, 32.5vw), height: min(170px, 32.5vw)),
    ));

    aspect-ratio: 1/1;
}

div.foxy-project-info-logo-wrapper-shrink {
    @include generate-dynamic-styles-with-hash((
        xxxl: (height: 280px, width: 280px, min-width: 280px, margin-right: 3rem),
        xl:   (height: 250px, width: 250px, min-width: 250px, margin-right: 3rem),
        lg:   (height: min(200px, 35vw), min-width: 0, width: min(200px, 35vw), margin-right:0)
    ));
}

div.foxy-project-info-logo-wrapper .image-view {
    width: 100%;
    height: 100%;
    margin: 0 auto;
    border-radius: 20%;
    overflow: hidden;
}

div.foxy-project-info-content {
    @include generate-dynamic-styles-with-hash((
        xxxl: (text-align: justify),
        lg:   (text-align: center)
    ));
}
</style>