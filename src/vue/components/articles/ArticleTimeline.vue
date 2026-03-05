<template>
    <article class="foxy-timeline-article">
        <ul class="foxy-timeline">
            <slot/>

            <ItemTimelineEntry :trailing="true"/>
        </ul>
    </article>
</template>

<script setup>
import ItemTimelineEntry from "/src/vue/components/articles/items/ItemTimelineEntry.vue"
</script>
