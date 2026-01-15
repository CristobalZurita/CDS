<template>
    <PageWrapper id="foxy-policy-page"
                 :no-padding="false"
                 :sections="sections"/>
</template>

<script setup>
import PageWrapper from "/src/vue/components/layout/PageWrapper.vue"
import SectionInfo from "/src/models/SectionInfo.js"
import PolicySection from "/src/vue/content/sections/PolicySection.vue"

const sections = [
    new SectionInfo('policy', PolicySection)
]
</script>

<style lang="scss" scoped>
</style>