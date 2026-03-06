<template>
    <div :style="backgroundStyles">
        <div :style="overlayStyles"/>
    </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
    faded: Boolean
})

const backgroundStyles = computed(() => ({
    position: 'absolute',
    height: 'calc(100% + 4rem)',
    width: '100%',
    zIndex: '-1',
    backgroundImage: 'url(/src/assets/header-bg.webp)',
    backgroundPosition: 'center',
    backgroundSize: 'cover'
}))

const overlayStyles = computed(() => {
    const baseStyles = {
        position: 'relative',
        height: '100%',
        width: '100%'
    }

    if (props.faded) {
        return {
            ...baseStyles,
            backgroundImage: 'linear-gradient(180deg, rgba(62, 60, 56, 0.83) 0%, rgba(62, 60, 56, 0.93) 30%, rgba(62, 60, 56, 0.99) 60%, rgba(62, 60, 56, 1) 100%)'
        }
    }

    return {
        ...baseStyles,
        backgroundImage: 'linear-gradient(180deg, rgba(62, 60, 56, 0.73) 0%, rgba(62, 60, 56, 0.86) 30%, rgba(62, 60, 56, 0.99) 60%, rgba(62, 60, 56, 1) 100%)'
    }
})
</script>
