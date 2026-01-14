<template>
    <!-- Sección del Equipo -->
    <PageSection variant="primary"
                 :id="props.id">
        <!-- Título -->
        <PageSectionHeader title="Nuestro *Equipo*"
                           subtitle="Conoce a las personas detrás del taller"/>

        <!-- Contenido -->
        <PageSectionContent>
            <ArticleTeamMembers>
                <ItemTeamMember name="Cristóbal Zurita"
                                role="Fundador y Técnico"
                                image="/images/team/team-1.jpg"
                                :links="[
                                    {faIcon:`fa-brands fa-instagram`, href:`https://www.instagram.com/cirujanodesintetizadores/`},
                                    {faIcon:`fa-brands fa-facebook`, href:`https://www.facebook.com/Cirujanodesintetizadores/`},
                                ]"/>
            </ArticleTeamMembers>
        </PageSectionContent>
    </PageSection>
</template>

<script setup>
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionHeader from "/src/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"
import ArticleTeamMembers from "/src/vue/components/articles/ArticleTeamMembers.vue"
import ItemTeamMember from "/src/vue/components/articles/items/ItemTeamMember.vue"

const props = defineProps({
    id: String
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
</style>
