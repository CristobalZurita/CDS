<template>
    <article class="foxy-custom-content-article"
             :class="props.class">
        <slot/>
    </article>
</template>

<script setup>
const props = defineProps({
    class: String
})
</script>
