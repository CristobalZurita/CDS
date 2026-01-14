<template>
    <div class="quoted-text">
        <span class="first-span" v-html="firstSpanContent"/>
        <span class="last-span" v-html="lastSpanContent"/>
    </div>
</template>

<script setup>
import {computed} from "vue"

const props = defineProps({
    text: String
})

const firstPart = computed(() => {
    const words = props.text.trim().split(/\s+/)
    return words.length >= 2 ? words[0] + " " : ""
})

const middlePart = computed(() => {
    const words = props.text.trim().split(/\s+/)
    return words.length > 2 ? words.slice(1, -1).join(" ") : ""
})

const lastPart = computed(() => {
    const words = props.text.trim().split(/\s+/)
    return words.length > 0 ? " " +  words[words.length - 1] : ""
})

const firstSpanContent = computed(() => {
    return `<i class="fa-solid fa-quote-left text-primary me-1"></i> ${firstPart.value} ${middlePart.value}`
})

const lastSpanContent = computed(() => {
    return `${lastPart.value} <i class="fa-solid fa-quote-right text-primary ms-1"></i>`
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

span.last-span {
    white-space: nowrap;
}
</style>