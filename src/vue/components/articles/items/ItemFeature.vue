<template>
    <div class="foxy-item-feature col-12 col-md-6 col-lg-4">
        <div class="foxy-item-feature-content mb-lg-4">
            <div class="foxy-item-feature-icon-wrapper">
                <CircleIcon :fa-icon="faIcon"/>
            </div>

            <div class="foxy-item-feature-content-wrapper">
                <h5 v-html="parsedTitle" class="mb-1 mb-sm-2 foxy-feature-title"/>

                <p class="text-muted text-4 mb-0 foxy-feature-description"
                   v-html="parsedDescription"/>
            </div>
        </div>
    </div>
</template>

<script setup>
import {computed} from "vue"
import {useUtils} from "/src/composables/utils.js"
import CircleIcon from "/src/vue/components/widgets/CircleIcon.vue"

const utils = useUtils()

const props = defineProps({
    title: String,
    faIcon:String,
    description: String
})

const parsedTitle = computed(() => {
    return utils.parseCustomText(props.title)
})

const parsedDescription = computed(() => {
    return utils.parseCustomText(props.description)
})
</script>
