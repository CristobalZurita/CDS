<template>
    <hr :style="dividerStyles"
        :class="props.class">
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
    class: String
})

const dividerStyles = computed(() => ({
    width: '60px',
    color: 'black',
    opacity: '1',
    border: '2px solid black',
    margin: '0 auto',
    backgroundColor: 'black'
}))
</script>
