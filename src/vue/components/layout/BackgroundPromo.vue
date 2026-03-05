<template>
    <div class="foxy-promo-background">
        <div :class="`foxy-promo-background-overlay-${faded ? `faded` : `default`}`"/>
    </div>
</template>

<script setup>
const props = defineProps({
    faded: Boolean
})
</script>
