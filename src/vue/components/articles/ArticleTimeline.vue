<template>
    <article class="foxy-timeline-article">
        <ul class="foxy-timeline">
            <slot/>

            <ItemTimelineEntry :trailing="true"/>
        </ul>
    </article>
</template>

<script setup>
import ItemTimelineEntry from "/src/vue/components/articles/items/ItemTimelineEntry.vue"
</script>

<style lang="scss">
@import "/src/scss/_theming.scss";

:root {
    --padding: 0 1rem;
    --image-dimensions: 180px;
    --min-item-height: 250px;
    --min-item-width: 42%;
    --item-padding: 0 1.5rem;

    --line-width: 4px;
    --line-position: 50%;
    --inverted-float: left;
    --inverted-align: right;

    @include media-breakpoint-down(xl) {
        --image-dimensions: 150px;
        --min-item-height: 220px;
        --min-item-width: 40%;
        --item-padding: 0 0.5rem;
    }

    @include media-breakpoint-down(lg) {
        --image-dimensions: 120px;
        --min-item-height: 200px;
        --min-item-width: 38%;
        --item-padding: 0 0rem;
    }

    @include media-breakpoint-down(md) {
        --padding: 0;
        --image-dimensions: min(80px, 20vw);
        --min-item-height: 150px;
        --min-item-width: 100%;
        --item-padding: 0 calc(var(--image-dimensions)/4) 0 calc(var(--image-dimensions)*1.2);

        --line-width: 2px;
        --line-position: calc(var(--image-dimensions)/2);
        --inverted-float: right;
        --inverted-align: left;
    }
}

ul.foxy-timeline {
    position: relative;
    padding: var(--padding);
    list-style: none;
}

ul.foxy-timeline:before {
    position: absolute;
    top: 0;
    bottom: 0;
    left: var(--line-position);
    width: var(--line-width);
    margin-left: calc(-1*var(--line-width)/2);
    content: "";
    height: calc(100% - var(--min-item-height)/3 + var(--image-dimensions)/3);
    background-color: $light-2
}
</style>