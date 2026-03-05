<template>
    <hr class="solid-divider"
        :class="props.class">
</template>

<script setup>
const props = defineProps({
    class: String
})
</script>
