<template>
    <div class="foxy-footer-block" :class="className">
        <div class="container-xxl">
            <div v-if="row" class="row foxy-footer-row">
                <slot/>
            </div>

            <slot v-else/>
        </div>
    </div>
</template>

<script setup>
import {computed} from "vue"

const props = defineProps({
    darken: Boolean,
    row: Boolean,
})

const className = computed(() => {
    return props.darken ?
        "foxy-footer-block-darken" :
        ""
})
</script>

<style lang="scss" scoped>
@use '@/scss/theming' as *;

div.foxy-footer-block {
    min-height: 40px;
    background-color: $footer-bg-color;
    padding: 2.25rem 0;
    text-align: center;
    &-darken {
        background-color: $footer-bg-highlight-color;
    }
}

div.foxy-footer-row {
    padding: 1.5rem 0;
    row-gap: 2rem;
    align-items: flex-start;

    @include media-breakpoint-up(lg) {
        padding: 2.5rem 0 3rem;
        text-align: left;
    }
}
</style>
