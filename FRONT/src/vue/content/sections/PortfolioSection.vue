<template>
    <!-- Sección de Portafolio -->
    <PageSection variant="default"
                 :id="props.id">
        <!-- Título -->
        <PageSectionHeader title="Nuestro *Portafolio*"
                           subtitle="Conoce algunos de nuestros trabajos"/>

        <!-- Contenido -->
        <PageSectionContent>
            <ArticlePortfolio :projects="projects"
                              :categories="categories"
                              :link-label="strings.get('where_to_find')"/>
        </PageSectionContent>
    </PageSection>
</template>

<script setup>
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionHeader from "/src/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"
import ArticlePortfolio from "/src/vue/components/articles/ArticlePortfolio.vue"
import {useStrings} from "/src/composables/strings.js"

const strings = useStrings()

const props = defineProps({
    id: String
})

const categories = [
    {id: 'synths', label: 'Sintetizadores'},
    {id: 'drums', label: 'Drum Machines'},
    {id: 'keys', label: 'Teclados'},
    {id: 'fx', label: 'Efectos'},
]

const projects = [
    {
        id: 1,
        title: 'Reparación Korg minilogue',
        category: 'keyboard',
        description: 'Restauración completa de síntesis y circuitería analógica',
        image: '/images/portfolio/korg-minilogue.jpg',
        status: 'completed',
        date: '2025-11-15'
    },
    {
        id: 2,
        title: 'Mantenimiento Roland TR-808',
        category: 'drums',
        description: 'Revisión de circuitos osciladores y ajuste de síntesis',
        image: '/images/portfolio/roland-tr808.jpg',
        status: 'completed',
        date: '2025-10-20'
    },
    {
        id: 3,
        title: 'Restauración Yamaha DX7',
        category: 'keyboard',
        description: 'Reparación de teclado y restauración de circuitos analógicos',
        image: '/images/portfolio/yamaha-dx7.jpg',
        status: 'completed',
        date: '2025-09-08'
    },
    {
        id: 4,
        title: 'Diagnóstico Moog Subsequent 37',
        category: 'keyboard',
        description: 'Análisis técnico y reparación de módulos de síntesis',
        image: '/images/portfolio/moog-sub37.jpg',
        status: 'in-progress',
        date: '2025-12-01'
    }
]
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
</style>
