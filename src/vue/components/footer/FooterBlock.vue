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
@import "/src/scss/_theming.scss";

div.foxy-footer-block {
    min-height: 40px;
    background-color: $footer-bg-color;
    padding: 1rem 0;
    text-align: center;
    &-darken {
        background-color: $footer-bg-highlight-color;
    }
}

div.foxy-footer-row {
    padding: 1rem 0;
}
</style>