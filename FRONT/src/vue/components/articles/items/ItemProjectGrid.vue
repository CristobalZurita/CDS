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

const layout = useLayout()
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

<style lang="scss">
@import "/src/scss/_theming.scss";

div.foxy-project-item {
    display: inline-flex;
    flex-direction: column;
    position: relative;
    margin-top: calc(var(--project-logo-size)/3);
    cursor: pointer;

    &-hidden {
        opacity: 0;
    }

    &-appear {
        animation: appear 0.3s ease-out forwards;
    }
}

@keyframes appear {
    from {
        opacity:0;
        transform: scale(0.3) translateY(-30%);
    }
    to {
        opacity:1
    }
}

div.foxy-project-item-thumb-wrapper {
    position: relative;
    margin: 0 auto;
    cursor: pointer;
    height: var(--project-logo-size);
    width: var(--project-logo-size);
    overflow: hidden;
    border-radius: 25%;

    & .image-view {
        width: 100%;
        height: 100%;
    }
}

div.foxy-project-item-thumb-overlay {
    position: absolute;
    top: 0;
    opacity: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    width: 100%;
    height: 100%;
    border-radius: 25%;

    background: fade-out(lighten($primary, 5%), 0.1);
    transition: all ease-in-out 0.25s;

    &-content {
        color: $white;
    }
}

button.foxy-project-item-title {
    border: none;
    padding: 0;
    background-color: transparent;
    color: $dark;

    margin: calc(var(--project-logo-size)/12) 0 0;
    font-size: calc(var(--project-logo-size)/7.8);
    font-family: $headings-font-family;
    @include media-breakpoint-down(lg) {
        margin: calc(var(--project-logo-size)/12) 0 0;
        font-size: calc(var(--project-logo-size)/6.1);
    }
}

p.foxy-project-item-category {
    margin: 0;
    padding: 0;

    font-size: calc(var(--project-logo-size)/10.5);
    @include media-breakpoint-down(lg) {
        font-size: calc(var(--project-logo-size)/7.5);
    }
}

div.foxy-project-item:hover {
    div.foxy-project-item-thumb-overlay {
        opacity: 1;
    }

    button.foxy-project-item-title {
        color: lighten($primary, 10%);
        transition: color ease-in-out 0.3s;
    }
}

</style>