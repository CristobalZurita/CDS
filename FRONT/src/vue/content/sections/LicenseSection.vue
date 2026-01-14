<template>
    <!-- Sección de Licencia -->
    <PageSection variant="default"
                 :id="props.id">
        <Breadcrumbs/>

        <PageSectionHeader title="*Términos* y Condiciones"
                           subtitle="Licencia de uso y atribuciones"/>

        <PageSectionContent>
            <ArticleParagraph title=""
                              fa-icon=""
                              :description="[
                                  `Este sitio web fue desarrollado utilizando tecnologías de código abierto. El template base está licenciado bajo la <a href='https://opensource.org/licenses/MIT'>licencia MIT</a>, lo que permite su uso, modificación y distribución siempre que se incluya el aviso de copyright correspondiente.`
                              ]"/>

            <ArticleParagraph title="Uso del sitio"
                              fa-icon="pi pi-briefcase"
                              :description="[
                                  `Este sitio web es propiedad de Cirujano de Sintetizadores y tiene como objetivo informar sobre los servicios de reparación, restauración y modificación de equipos de audio electrónico.`,
                                  `El contenido de este sitio, incluyendo textos, imágenes y diseño, está protegido por derechos de autor. No está permitida su reproducción sin autorización previa.`
                              ]"/>

            <ArticleParagraph title="Servicios"
                              fa-icon="pi pi-wrench"
                              :description="[
                                  `Los servicios ofrecidos por Cirujano de Sintetizadores incluyen diagnóstico, reparación, restauración, modificación y mantenimiento de sintetizadores, teclados, drum machines y otros equipos de audio profesional.`,
                                  `Cada trabajo se realiza bajo presupuesto previo aprobado por el cliente. Los plazos de entrega y garantías se especifican en cada cotización según el tipo de trabajo a realizar.`
                              ]"/>

            <ArticleParagraph title="Responsabilidad"
                              fa-icon="pi pi-exclamation-triangle"
                              :description="[
                                  `Cirujano de Sintetizadores no se hace responsable por equipos abandonados después de 90 días de notificada la finalización del trabajo o el presupuesto rechazado.`,
                                  `El cliente es responsable del embalaje adecuado para envíos. Los costos de envío corren por cuenta del cliente tanto para la entrega como para la devolución del equipo.`
                              ]"/>

            <ArticleParagraph title="Contacto"
                              fa-icon="pi pi-envelope"
                              :description="[
                                  `Para consultas sobre estos términos y condiciones, puedes contactarnos a través del formulario de contacto en este sitio o mediante nuestras redes sociales oficiales.`
                              ]"/>
        </PageSectionContent>
    </PageSection>
</template>

<script setup>
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionHeader from "/src/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"
import ArticleParagraph from "/src/vue/components/articles/ArticleParagraph.vue"
import Breadcrumbs from "/src/vue/components/widgets/Breadcrumbs.vue"

const props = defineProps({
    id: String
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
</style>
