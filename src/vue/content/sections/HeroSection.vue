<template>
    <!-- Heading Section -->
    <PageHeader :id="props.id"
                title="*<strong>MANTENCIÓN</strong>* *<strong>RESTAURACIÓN</strong>* *<strong>REPARACIÓN</strong>*"
                subtitle=""
                logo-url="/images/logo/NUEVO_cirujano.png"
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

<style lang="scss" scoped>
</style>
