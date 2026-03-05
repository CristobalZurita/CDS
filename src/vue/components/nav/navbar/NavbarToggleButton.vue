<template>
    <button class="foxy-navbar-toggle"
            :class="collapsed ? `closed` : `open`"
            type="button">
        <i :class="icon"
           class="ms-1 me-1"/>
    </button>
</template>

<script setup>
import {computed} from "vue"

const props = defineProps({
    collapsed: Boolean
})

const icon = computed(() => {
    return props.collapsed ?
        `fas fa-bars` :
        `fas fa-minimize`
})
</script>
