<template>
    <div class="alert text-4 mb-0"
         :class="`alert-${props.variant || 'primary'}`">
        <i class="me-2"
           :class="faIcon"/>

        <span v-html="message"/>
    </div>
</template>

<script setup>
import {computed} from "vue"

const props = defineProps({
    variant: String,
    message: String,
})

const faIcon = computed(() => {
    const iconMap = {
        success: "fa-solid fa-check-circle",
        danger: "fa-solid fa-exclamation-triangle",
    }

    return iconMap[props.variant]
        || "fa-solid fa-info-circle"
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
</style>