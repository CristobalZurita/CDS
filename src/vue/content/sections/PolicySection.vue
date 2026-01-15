<template>
    <!-- Sección de Política de Privacidad -->
    <PageSection variant="default"
                 :id="props.id">
        <Breadcrumbs/>

        <PageSectionHeader title="Política de *Privacidad*"
                           subtitle="Cómo manejamos tu información"/>

        <PageSectionContent>
            <ArticleParagraph title=""
                              faIcon=""
                              :description="[
                                  `Esta Política de Privacidad explica cómo se recopila, almacena, utiliza y gestiona la información que proporcionas mientras navegas en este sitio.`,
                                  `Al acceder a este sitio, estás consintiendo la recopilación y uso de tu información personal según lo descrito en esta Política de Privacidad. Ten en cuenta que esta Política puede actualizarse periódicamente, por lo que te recomendamos revisar esta página con frecuencia.`
                              ]"/>

            <ArticleParagraph title="Información recopilada"
                              faIcon="pi pi-address-book"
                              :description="[
                                  `La información que proporcionas voluntariamente puede ser recopilada y almacenada cuando accedes a este sitio. Esto puede incluir datos de contacto como nombre y correo electrónico cuando utilizas el formulario de contacto.`,
                                  `Además, se puede recopilar información adicional cada vez que accedes al servicio, como direcciones de protocolo de internet, tipo de dispositivo, idioma del dispositivo, tipo de plataforma, páginas visitadas y la fecha y hora de esta actividad. Esta información se utiliza para mejorar tu experiencia en el sitio.`,
                                  `Te aseguramos que cualquier dato recopilado no será divulgado, alquilado, prestado, vendido o distribuido voluntariamente a terceros. Se utilizará únicamente para fines analíticos y para mejorar tu experiencia de uso.`
                              ]"/>

            <ArticleParagraph title="Cookies"
                              faIcon="pi pi-database"
                              :description="[
                                  `Una cookie es un pequeño archivo de datos que se almacena en el disco duro de tu dispositivo. Permite que la aplicación identifique rápidamente tu dispositivo y recupere tu información y preferencias de usuario.`,
                                  `Toda la información contenida en una cookie puede estar vinculada a tu información personal, y estos datos pueden usarse para guardar tus preferencias y mejorar la usabilidad general del sitio. Si lo deseas, puedes desactivar las cookies en cualquier momento.`
                              ]"/>

            <ArticleParagraph title="Seguridad"
                              faIcon="pi pi-lock"
                              :description="[
                                  `La seguridad de tu información personal se toma en serio, y se han implementado medidas técnicas y organizativas razonables para protegerla de pérdida accidental, acceso no autorizado, alteración o divulgación.`,
                                  `Sin embargo, no se puede garantizar que terceros no autorizados nunca puedan vulnerar estas medidas o usar tu información personal para propósitos indebidos. Es importante tener en cuenta que el correo electrónico y los sistemas de mensajería no se consideran seguros, por lo que se aconseja no compartir información personal a través de estos medios.`
                              ]"/>

            <ArticleParagraph title="Enlaces"
                              faIcon="pi pi-link"
                              :description="[
                                  `Este sitio puede contener enlaces a otros sitios web. Ten en cuenta que el hecho de que este sitio enlace a otro sitio web no implica que lo respalde o autorice. Tampoco es una representación de ningún tipo de afiliación con ese tercero.`,
                                  `Las políticas de privacidad de otros sitios web a los que se pueda acceder desde este sitio no son nuestra responsabilidad. Por lo tanto, se recomienda leer cuidadosamente las políticas de privacidad de dichos sitios antes de salir de esta página.`
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
