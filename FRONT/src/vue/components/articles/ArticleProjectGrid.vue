<template>
    <article class="foxy-project-grid-article row g-0 text-center">
        <!-- Filters -->
        <div class="col-12 mb-2">
            <FilterTabs :items="categories"
                        @selected="_onCategorySelected"/>
        </div>

        <!-- Items -->
        <div class="col-12 foxy-project-grid-container">
            <div class="foxy-project-grid row mb-4">
                <div v-for="(item, index) in filteredItems"
                     :key="index"
                     class="foxy-project-grid-item-wrapper col-4 col-lg-3 text-center">
                    <component :is="item"
                               :index="index"
                               :transition-count="refreshTimes"/>
                </div>
            </div>
        </div>
    </article>
</template>

<script setup>
import FilterTabs from "/src/vue/components/widgets/FilterTabs.vue"
import {computed, ref, useSlots} from "vue"
import {useStrings} from "/src/composables/strings.js"
import {useLayout} from "/src/composables/layout.js"

const strings = useStrings()
const layout = useLayout()
const slots = useSlots()

const selectedCategoryId = ref(null)
const refreshTimes = ref(0)

const items = computed(() => {
    return slots.default()
})

const filteredItems = computed(() => {
    const allItems = items.value
    if(!allItems || allItems.length === 0)
        return []

    return allItems.filter(item => {
        return item.props.category === selectedCategoryId.value
        || !selectedCategoryId.value
        || selectedCategoryId.value === strings.get("all_categories")
    })
})

const categories = computed(() => {
    return [strings.get("all_categories"), ...new Set(items.value.map(item => item.props.category))].filter(category => category)
})

const _onCategorySelected = (categoryId) => {
    if(categoryId === selectedCategoryId.value)
        return

    refreshTimes.value++
    selectedCategoryId.value = categoryId
}
</script>

<style lang="scss">
@import "/src/scss/_theming.scss";

:root {
    --project-logo-size: min(clamp(140px, 20vh, 170px), clamp(140px, 10.5vw, 170px));
    @include media-breakpoint-down(lg) {
        --project-logo-size: min(clamp(80px, 20vh, 110px), clamp(70px, 20.5vw, 110px));
    }
}

div.foxy-project-grid {
    min-height: calc(var(--project-logo-size) * 3.5);
}
</style>