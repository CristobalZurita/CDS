<template>
    <PageWrapper id="foxy-calculators-page"
                 :no-padding="false"
                 :sections="sections"/>
</template>

<script setup>
import PageWrapper from "/src/vue/components/layout/PageWrapper.vue"
import SectionInfo from "/src/models/SectionInfo.js"
import CalculatorsSection from "/src/vue/content/sections/CalculatorsSection.vue"

const sections = [
    new SectionInfo('calculators', CalculatorsSection, 'Calculadoras', 'pi pi-calculator')
]
</script>
