<template>
    <!-- About Section -->
<PageSection variant="promo"
             :id="props.id">

  <PageSectionContent>
    <ArticleCustomContent>
      <!-- Último trabajo -->
      <ProjectInfo image="/images/portfolio/ultimo-trabajo-juno106.jpg">
        <ProjectInfoFeaturedContent
          title="*Último trabajo*"
          description="
            <b>Restauración integral de un Roland Juno-106 (1984)</b>.<br><br>
            Este sintetizador llegó al taller con ruido constante en la salida, varias voces mudas, sliders rasposos y una afinación inestable después de algunos minutos de uso. Venía de años guardado, con polvo interno, capacitores secos en la fuente de poder y varios módulos 80017A deteriorados.<br><br>
            En <b>Cirujano de Sintetizadores</b> se realizó limpieza profunda, recap de la fuente, revisión completa de la etapa de audio, reemplazo de los 80017A por módulos de reemplazo actuales, limpieza y lubricación de faders y teclas, más una calibración fina de filtro, VCA y afinación global.<br><br>
            El resultado es un Juno-106 silencioso, estable y confiable, listo para volver al escenario y al estudio con su carácter clásico, pero con la seguridad de un instrumento recién puesto a punto."
          :links="[
            { label: `Ver galería del trabajo`, href: `#fotos`, faIcon:`fa-solid fa-camera` },
            { label: `Agenda tu evaluación`, href: `#contact`, faIcon:`fa-solid fa-envelope` }
          ]"
        />
      </ProjectInfo>
    </ArticleCustomContent>
  </PageSectionContent>
</PageSection>

</template>

<script setup>
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"
import ArticleCustomContent from "/src/vue/components/articles/ArticleCustomContent.vue"
import ProjectInfo from "/src/vue/components/projects/ProjectInfo.vue"
import ProjectInfoFeaturedContent from "/src/vue/components/projects/ProjectInfoFeaturedContent.vue"

const props = defineProps({
    id: String
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
</style>