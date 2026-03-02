<template>
    <li class="foxy-timeline-item"
        :class="trailing ? `foxy-timeline-item-trailing` : ``">
        <!-- Image -->
        <div class="foxy-timeline-image-wrapper"
             :class="trailing ? `foxy-timeline-image-wrapper-sm` : ``">
            <ImageView v-if="props.image"
                       :src="props.image"
                       :alt="props.title"/>
        </div>

        <!-- Panel -->
        <div v-if="title || description"
             class="foxy-timeline-panel"
             :class="{'foxy-timeline-panel-inverted': inverted}">
            <div class="heading">
                <!-- Title -->
                <h3 class="mb-1"
                    v-html="parsedTitle"/>

                <!-- Date -->
                <span v-if="date"
                      class="badge bg-transparent text-dark text-2 mb-2 mb-xxl-3 mt-1 px-0">
                    <i class="fa-regular fa-calendar me-2 ms-1"/>
                    <span v-html="date" class="me-1"/>
                </span>
            </div>

            <div v-if="description" class="content">
                <!-- Description -->
                <p class="text-muted text-4"
                   v-html="parsedDescription"/>
            </div>
        </div>
    </li>
</template>

<script setup>
import {useUtils} from "/src/composables/utils.js"
import ImageView from "/src/vue/components/generic/ImageView.vue"
import {computed} from "vue"

const utils = useUtils()

const props = defineProps({
    title: String,
    dateStart: String,
    dateEnd: String,
    image: String,
    description: String,
    inverted: Boolean,
    trailing: Boolean
})

const parsedTitle = computed(() => {
    return utils.parseCustomText(props.title)
})

const parsedDescription = computed(() => {
    return utils.parseCustomText(props.description)
})

const date = computed(() => {
    if(!props.dateEnd)
        return props.dateStart

    return `${props.dateStart} <i class="fa-solid fa-arrow-right-long mx-1 timeline-arrow-icon"></i> ${props.dateEnd}`
})
</script>
