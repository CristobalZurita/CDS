<template>
    <!-- Sección de Opiniones -->
    <PageSection variant="primary"
                 :id="props.id">
        <!-- Título -->
        <PageSectionHeader title="Opiniones de *Clientes*"
                           subtitle="Lo que dicen quienes han confiado en nosotros"/>

        <!-- Contenido -->
        <PageSectionContent>
            <ArticleTestimonials>
                <ItemTestimonial title="Instagram"
                                 image="/images/clients/client-instagram.svg"
                                 quote="Llevé mi <b>Juno-106</b> que llevaba años sin funcionar y lo dejaron como nuevo. <b>Excelente diagnóstico</b> y muy buena comunicación durante todo el proceso. 100% recomendado para cualquier sintetizador vintage."
                                 author="Músico Independiente"
                                 role="Valparaíso"/>

                <ItemTestimonial title="Facebook"
                                 image="/images/clients/client-facebook.svg"
                                 quote="<b>Profesionalismo y pasión</b> por los sintetizadores. Me repararon un Korg M1 que otros técnicos no pudieron arreglar. El trabajo fue impecable y el precio muy justo."
                                 author="Productor Musical"
                                 role="Santiago"/>

                <ItemTestimonial title="Instagram"
                                 image="/images/clients/client-instagram.svg"
                                 quote="Necesitaba una <b>modificación especial</b> para mi drum machine y no solo lo hicieron perfecto, sino que me explicaron todo el proceso. <b>Gran conocimiento técnico</b> y muy buen trato."
                                 author="DJ & Productor"
                                 role="Viña del Mar"/>
            </ArticleTestimonials>
        </PageSectionContent>

        <!-- Footer con redes sociales -->
        <PageSectionFooter title="Síguenos en *Redes Sociales*"
                           description="Encuentra más de nuestro trabajo y novedades en nuestras redes oficiales."
                           :include-divider="true"
                           :description-text-class="`text-3`"
                           button-label="Instagram"
                           button-fa-icon="fa-brands fa-instagram"
                           button-url="https://www.instagram.com/cirujanodesintetizadores/"/>
    </PageSection>
</template>

<script setup>
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionHeader from "/src/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"
import PageSectionFooter from "/src/vue/components/layout/PageSectionFooter.vue"
import ArticleTestimonials from "/src/vue/components/articles/ArticleTestimonials.vue"
import ItemTestimonial from "/src/vue/components/articles/items/ItemTestimonial.vue"

const props = defineProps({
    id: String
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
</style>
