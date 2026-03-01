<template>
    <footer class="foxy-footer">
        <slot/>
    </footer>
</template>

<script setup>
</script>

<style lang="scss">
@use '@/scss/theming' as *;

.foxy-footer {
    background-color: $footer-bg-color;
}
</style>