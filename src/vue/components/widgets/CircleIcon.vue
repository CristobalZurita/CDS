<template>
    <!-- Icon Stack -->
    <span class="icon-stack fa-stack">
        <i class="fas fa-circle fa-stack-2x text-primary"/>
        <i class="fa-stack-1x fa-inverse" :class="props.faIcon"/>
    </span>
</template>

<script setup>
/**
 * @property {String} faIcon
 */
const props = defineProps({
    faIcon: String
})
</script>
