<template>
    <footer class="foxy-footer">
        <slot/>
    </footer>
</template>

<script setup>
</script>

<style lang="scss">
@import "/src/scss/_theming.scss";

.foxy-footer {
    background-color: $footer-bg-color;
}
</style>