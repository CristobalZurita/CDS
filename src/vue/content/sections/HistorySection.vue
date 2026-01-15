<template>
    <!-- Services Section -->
    <PageSection variant="default"
                 :id="props.id">

        <!-- Content -->
       <PageSectionHeader title="Nuestra *Historia*"
                   subtitle="Cómo nació y creció Cirujano de Sintetizadores"/>

<PageSectionContent>
  <ArticleTimeline>
    <ItemTimelineEntry
      title="El origen del taller"
      dateStart="2014"
      dateEnd=""
      image="/images/history/history-1.png"
      description="Alrededor de 2014, mientras exploraba la música electrónica con sintetizadores y drum machines, nació una necesidad clara: casi no existían técnicos especializados en estos instrumentos. De esa búsqueda por reparar mis propias máquinas surge la idea de crear un taller dedicado exclusivamente a equipos musicales electrónicos."
      :inverted="true"
    />

    <ItemTimelineEntry
      title="Formación y especialización"
      dateStart="Años siguientes"
      dateEnd=""
      image="/images/history/history-2.png"
      description="Para dar un soporte profesional a este oficio me formé como Técnico en Automatización Industrial en Duoc, complementando esa base con mi experiencia como percusionista clásico y marimbista de la Universidad de Chile. Esa doble mirada —ingeniería y música— definió el sello de Cirujano de Sintetizadores."
      :inverted="false"
    />

    <ItemTimelineEntry
      title="Luthería electrónica en la práctica"
      dateStart="Consolidación del oficio"
      dateEnd=""
      image="/images/history/history-3.png"
      description="Con los años el taller amplió su campo de acción: teclados, pianos eléctricos, sintetizadores, Clavinovas, drum machines, procesadores de efecto, pedales y sistemas de audio. El trabajo se fue enfocando en una luthería electrónica detallista, respetando el carácter sonoro original de cada equipo y mejorando su confiabilidad."
      :inverted="true"
    />

    <ItemTimelineEntry
      title="Taller en Providencia"
      dateStart="Etapa Santiago"
      dateEnd=""
      image="/images/history/history-4.png"
      description="Durante un año el taller funcionó como local comercial en un importante caracol de la comuna de Providencia, en pleno centro de Santiago. Esa etapa permitió consolidar procesos de trabajo, ampliar la experiencia con distintos modelos y atender a músicos y estudios de diversos estilos."
      :inverted="false"
    />

    <ItemTimelineEntry
      title="Valparaíso y proyección"
      dateStart="Actualidad"
      dateEnd=""
      image="/images/history/history-5.png"
      description="Hoy Cirujano de Sintetizadores está radicado en Valparaíso, ofreciendo servicio especializado a la Quinta Región y a clientes de diferentes ciudades de Chile. Cada reparación se aborda con criterio profesional, mediciones rigurosas y pruebas en contexto musical, buscando siempre entregar la mejor experiencia posible a cada músico."
      :inverted="true"
    />
  </ArticleTimeline>
</PageSectionContent>

    </PageSection>
</template>

<script setup>
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionHeader from "/src/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"
import ArticleTimeline from "/src/vue/components/articles/ArticleTimeline.vue"
import ItemTimelineEntry from "/src/vue/components/articles/items/ItemTimelineEntry.vue"

const props = defineProps({
    id: String
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
</style>