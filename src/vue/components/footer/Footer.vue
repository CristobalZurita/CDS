<template>
    <footer :style="footerStyles">
        <slot/>
    </footer>
</template>

<script setup>
import { computed } from "vue"
import { COLORS } from "@/composables/useResponsive"

const footerStyles = computed(() => ({
    backgroundColor: COLORS.footerBg
}))
</script>
