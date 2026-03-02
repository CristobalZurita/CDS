<template>
    <!-- Heading Section -->
    <PageHeader :id="props.id"
                title="*<strong>RESTAURACIÓN</strong>* <span class='hero-title-sep'>&bull;</span> *<strong>MANTENCIÓN</strong>* <span class='hero-title-sep'>&bull;</span> *<strong>REPARACIÓN</strong>*"
                subtitle=""
                logo-url="/images/logo/NUEVO_cirujano.webp"
                :show-button="false"
                :show-cta-buttons="true"
                @scroll-to-top="scrollToTop"/>
</template>

<script setup>
import PageHeader from "/src/vue/components/layout/PageHeader.vue"

const props = defineProps({
    id: String
})

const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>
