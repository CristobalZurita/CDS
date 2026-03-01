<template>
    <footer class="foxy-footer">
        <slot/>
    </footer>
</template>

<script setup>
</script>

<style lang="scss">
@use "@/scss/_theming.scss" as *;

.foxy-footer {
    background-color: $footer-bg-color;
}
</style>