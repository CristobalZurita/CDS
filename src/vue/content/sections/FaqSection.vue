<template>
    <!-- Sección de Preguntas Frecuentes -->
    <PageSection variant="default"
                 :id="props.id">
        <!-- Título -->
        <PageSectionHeader title="Preguntas *Frecuentes*"
                           subtitle="Respuestas rápidas a tus dudas"/>

        <!-- Contenido -->
        <PageSectionContent>
            <ArticleFaq>
                <ItemFaqQuestion question="¿Qué tipos de equipos reparan?"
                                 answer="Trabajamos con <b>sintetizadores analógicos y digitales</b>, drum machines, samplers, teclados electrónicos, controladores MIDI y equipos de audio profesional en general. Tenemos experiencia con marcas como <b>Roland, Korg, Yamaha, Moog, Sequential, Oberheim</b> y muchas más, tanto vintage como modernas."/>

                <ItemFaqQuestion question="¿Cómo funciona el proceso de reparación?"
                                 answer="Primero realizamos un <b>diagnóstico detallado</b> de tu equipo para identificar el problema. Te enviamos un presupuesto con el costo y tiempo estimado. Una vez aprobado, procedemos con la reparación. Durante todo el proceso mantenemos <b>comunicación constante</b> para informarte del avance."/>

                <ItemFaqQuestion question="¿Cuánto tiempo demora una reparación?"
                                 answer="El tiempo varía según la complejidad del problema y la <b>disponibilidad de repuestos</b>. Reparaciones simples pueden estar listas en <b>1-2 semanas</b>, mientras que trabajos más complejos o que requieren piezas especiales pueden tomar más tiempo. Siempre te informamos los plazos estimados en el presupuesto inicial."/>

                <ItemFaqQuestion question="¿Hacen envíos a otras ciudades?"
                                 answer="Sí, recibimos equipos de <b>todo Chile</b>. Puedes enviarnos tu equipo por encomienda y coordinamos la devolución una vez reparado. Los costos de envío corren por cuenta del cliente. Para equipos muy delicados o de gran valor, recomendamos <b>embalaje profesional</b>."/>

                <ItemFaqQuestion question="¿Realizan modificaciones o upgrades?"
                                 answer="¡Absolutamente! Además de reparaciones, ofrecemos <b>modificaciones y mejoras</b> como cambio de potenciómetros, instalación de salidas individuales, modificaciones de filtros, upgrades de memoria y más. Si tienes una idea específica, <b>consúltanos</b> y vemos cómo implementarla."/>

                <ItemFaqQuestion question="¿Qué garantía ofrecen?"
                                 answer="Todas nuestras reparaciones incluyen <b>garantía por el trabajo realizado</b>. El período de garantía depende del tipo de reparación y se especifica en cada presupuesto. Usamos <b>repuestos de calidad</b> y técnicas profesionales para asegurar resultados duraderos."/>
            </ArticleFaq>
        </PageSectionContent>

        <!-- Footer -->
        <PageSectionFooter title="¿Tienes otra *consulta*?"
                           description="Si no encontraste la respuesta que buscabas, no dudes en contactarnos directamente."
                           :include-divider="true"
                           :description-text-class="`text-3`"
                           button-label="Contáctanos"
                           button-fa-icon="fa-solid fa-envelope"
                           button-url="#contact"/>
    </PageSection>
</template>

<script setup>
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionHeader from "/src/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"
import PageSectionFooter from "/src/vue/components/layout/PageSectionFooter.vue"
import ArticleFaq from "/src/vue/components/articles/ArticleFaq.vue"
import ItemFaqQuestion from "/src/vue/components/articles/items/ItemFaqQuestion.vue"

const props = defineProps({
    id: String
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
</style>
