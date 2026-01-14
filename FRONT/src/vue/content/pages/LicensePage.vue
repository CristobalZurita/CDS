<template>
    <PageWrapper id="foxy-license-page"
                 :no-padding="false"
                 :sections="sections"/>
</template>

<script setup>
import PageWrapper from "/src/vue/components/layout/PageWrapper.vue"
import SectionInfo from "/src/models/SectionInfo.js"
import LicenseSection from "/src/vue/content/sections/LicenseSection.vue"

const sections = [
    new SectionInfo('license', LicenseSection)
]
</script>

<style lang="scss" scoped>
</style>