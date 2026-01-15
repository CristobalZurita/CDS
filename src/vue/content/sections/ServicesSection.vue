<template>
    <!-- Services Section -->
    <PageSection variant="primary"
                 :id="props.id">
        <!-- Title -->
        <PageSectionHeader
            title="Nuestros Servicios"
            subtitle="Volvemos a la vida tus equipos de audio con compromiso y pasión."
        />

        <!-- Content -->
        <PageSectionContent>
            <ArticleFeatures>
                <ItemFeature
                    title="Restauración y Reparación"
                    fa-icon="fa-solid fa-screwdriver-wrench"
                    description="Diagnóstico detallado, reparación electrónica y restauración estética de sintetizadores, teclados, drum machines y módulos, pedales, efectos y otros equipos de audio profesionales."
                />

                <ItemFeature
                    title="Cambio de Componentes"
                    fa-icon="fa-solid fa-microscope"
                    description="Reemplazo profesional de condensadores, potenciómetros, teclas, jacks, faders y otros componentes críticos como reguladores de voltaje, diodos y más."
                />

                <ItemFeature
                    title="Limpieza y Mantenimiento"
                    fa-icon="fa-solid fa-heart-circle-bolt"
                    description="Limpieza interna y externa, remoción de polvo y óxido, tratamiento de contactos y revisión general para mejorar el funcionamiento mecánico y eléctrico del instrumento."
                />

                <ItemFeature
                    title="Mantención Preventiva"
                    fa-icon="fa-solid fa-car-battery"
                    description="Servicio orientado a evitar fallas futuras: revisión de fuente de poder, chequeo de tensiones, ajuste de calibraciones y testeo prolongado para asegurar un funcionamiento estable."
                />

                <ItemFeature
                    title="Mantención Correctiva"
                    fa-icon="fa-solid fa-hand-sparkles"
                    description="Atención a fallas específicas: notas que no suenan, ruidos, inestabilidad, cuelgues, problemas de MIDI o audio. Localizamos la causa y aplicamos la solución más adecuada para cada caso."
                />

                <ItemFeature
                    title="Programación de Equipos"
                    fa-icon="fa-solid fa-code"
                    description="Configuración, actualización de firmware y programación de presets en sintetizadores, módulos y efectos, dejando tu set listo para tocar, grabar o girar sin perder tiempo en menúes."
                />
            </ArticleFeatures>
        </PageSectionContent>
    </PageSection>
</template>


<script setup>
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionHeader from "/src/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"
import ArticleFeatures from "/src/vue/components/articles/ArticleFeatures.vue"
import ItemFeature from "/src/vue/components/articles/items/ItemFeature.vue"

const props = defineProps({
    id: String
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
</style>