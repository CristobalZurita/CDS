<template>
    <div class="foxy-project-item"
         :class="{
            'foxy-project-item-hidden': !isShowing,
            'foxy-project-item-appear': isShowing,
         }"
         @click="_onItemSelected">
        <div class="foxy-project-item-thumb-wrapper">
            <ImageView :src="props.image"
                       :alt="props.title"
                       :spinner-enabled="false"
                       ref="imageView"
                       class="foxy-project-item-thumb"/>

            <div class="foxy-project-item-thumb-overlay">
                <div class="foxy-project-item-thumb-overlay-content eq-h6">
                    <i class="fas fa-eye fa-2x"/>
                </div>
            </div>
        </div>

        <div class="foxy-project-item-description-wrapper">
            <button class="foxy-project-item-title"
                    v-html="props.title"/>

            <p class="foxy-project-item-category text-muted"
               v-html="props.category"/>
        </div>
    </div>
</template>

<script setup>
import ImageView from "/src/vue/components/generic/ImageView.vue"
import {inject, onMounted, onUnmounted, ref, watch} from "vue"
import {useLayout} from "/src/composables/layout.js"

const _layout = useLayout()
const projectModalTarget = inject("projectModalTarget")

const props = defineProps({
    title: String,
    category: String,
    description: String,
    tags: Array,
    links: Array,
    image: String,
    index: Number,
    transitionCount: Number
})

const isShowing = ref(false)
const interval = ref(null)
const timeout = ref(null)
const imageView = ref(null)

onMounted(() => {
    _resetTransition()
    _appear()
})

onUnmounted(() => {
    _resetTransition()
})

watch(() => props.transitionCount, () => {
    _resetTransition()
    _appear()
})

const _resetTransition = () => {
    isShowing.value = false

    clearInterval(interval.value)
    interval.value = null

    clearTimeout(timeout.value)
    timeout.value = null
}

const _appear = () => {
    _checkLoadCompletion()
}

const _checkLoadCompletion = () => {
    interval.value = setInterval(() => {
        if(imageView.value && !imageView.value.isLoading()) {
            _scheduleTransition()
        }
    }, 1000/30)
}

const _scheduleTransition = () => {
    clearInterval(interval.value)
    interval.value = null

    const index = props.index || 0
    timeout.value = setTimeout(() => {
        isShowing.value = true
        clearTimeout(timeout.value)
        timeout.value = null
    }, 30 + index * 60)
}

const _onItemSelected = () => {
    projectModalTarget.value = {
        title: props.title,
        description: props.description,
        category: props.category,
        tags: props.tags,
        links: props.links,
        image: props.image
    }
}
</script>
