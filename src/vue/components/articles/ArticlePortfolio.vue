<template>
    <ArticleProjectGrid>
        <ItemProjectGrid
            v-for="project in normalizedProjects"
            :key="project.id || project.title"
            :title="project.title"
            :category="project.categoryLabel"
            :description="project.description"
            :image="project.image"
            :tags="project.tags"
            :links="project.links"
        />
    </ArticleProjectGrid>
</template>

<script setup>
import { computed } from "vue"
import ArticleProjectGrid from "/src/vue/components/articles/ArticleProjectGrid.vue"
import ItemProjectGrid from "/src/vue/components/articles/items/ItemProjectGrid.vue"

const props = defineProps({
    projects: { type: Array, default: () => [] },
    categories: { type: Array, default: () => [] },
    linkLabel: { type: String, default: "" }
})

const normalizedProjects = computed(() => {
    const categoriesById = new Map(
        (props.categories || []).map((category) => [category.id, category.label])
    )

    return (props.projects || []).map((project) => ({
        ...project,
        categoryLabel: categoriesById.get(project.category) || project.category || "General"
    }))
})
</script>

<style lang="scss" scoped>
@import "@/scss/_theming.scss";
</style>
