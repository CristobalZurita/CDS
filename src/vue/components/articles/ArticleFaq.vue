<template>
    <article class="foxy-info-block-faq">
        <!-- Row -->
        <div class="faq-grid">
            <template v-if="$slots.default">
                <div v-for="(child, index) in $slots.default()" class="faq-grid-item-wrapper">
                    <component :is="child" />
                </div>
            </template>
        </div>
    </article>
</template>

<script setup>
const props = defineProps({})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

div.faq-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    column-gap: 40px;
    row-gap: 30px;

    @include media-breakpoint-down(xxl) {
        grid-template-columns: repeat(1, 1fr);
        row-gap: 20px;
    }

    @include media-breakpoint-down(md) {
        row-gap: 10px;
    }
}

hr.foxy-info-block-faq-divider {
    opacity: 0.1;
}
</style>