<template>
    <article class="foxy-info-block-faq">
        <!-- Row -->
        <div class="faq-grid">
            <template v-if="$slots.default">
                <div v-for="(child, index) in $slots.default()" class="faq-grid-item-wrapper">
                    <component :is="child" />
                </div>
            </template>
        </div>
    </article>
</template>

<script setup>
const props = defineProps({})
</script>
