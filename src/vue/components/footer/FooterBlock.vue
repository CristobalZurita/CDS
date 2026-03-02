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
