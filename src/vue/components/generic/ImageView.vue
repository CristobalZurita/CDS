<template>
    <div class="image-view" :class="props.class">
        <img class="image"
             v-show="shouldShowImage"
             ref="img"
             :src="src"
             :alt="alt"
             @load="_onImageLoadSuccess"
             @error="_onImageLoadError"/>

        <Spinner v-if="props.spinnerEnabled"
                 v-show="shouldShowSpinner"
                 class="spinner"/>

        <div v-if="shouldShowFallback"
             class="image-not-found-fallback">
            <i class="fa-solid fa-eye-slash"/>
        </div>
    </div>
</template>

<script setup>
import {computed, ref, watch} from "vue"
import Spinner from "/src/vue/components/widgets/Spinner.vue"

const props = defineProps({
    src: String,
    alt: String,
    class: String,
    spinnerEnabled: Boolean
})

const LoadStatus = {
    LOADING: "loading",
    LOADED: "loaded",
    ERROR: "error"
}

const emit = defineEmits(["loaded", "error", "completed"])
const img = ref(null)
const loadStatus = ref(LoadStatus.LOADING)

const shouldShowImage = computed(() => { return loadStatus.value === LoadStatus.LOADED })
const shouldShowSpinner = computed(() => { return loadStatus.value === LoadStatus.LOADING })
const shouldShowFallback = computed(() => { return loadStatus.value === LoadStatus.ERROR })

watch(() => props.src, () => {
   loadStatus.value = LoadStatus.LOADING
})

const isLoading = () => {
    return loadStatus.value === LoadStatus.LOADING
}

const _onImageLoadSuccess = () => {
    loadStatus.value = LoadStatus.LOADED
    if(img.value) {
        img.value.setAttribute('load-status', LoadStatus.LOADED)
    }
    emit("loaded")
    emit("completed")
}

const _onImageLoadError = () => {
    // Try a gentle fallback for missing instrument photos: replace with brand/agency logo
    try {
        const currentSrc = img.value?.getAttribute('src') || props.src
        if (currentSrc && currentSrc.includes('/images/instrumentos/') && !currentSrc.includes('-fallback')) {
            // Attempt a single fallback to an agency logo
            const fallback = '/images/logo/agency-logo.webp'
            if (img.value) img.value.setAttribute('src', fallback)
            loadStatus.value = LoadStatus.LOADING
            return
        }
    } catch {
        // ignore and continue to error state
    }
    loadStatus.value = LoadStatus.ERROR
    if(img.value) {
        img.value.setAttribute('load-status', LoadStatus.ERROR)
    }
    emit("error")
    emit("completed")
}

defineExpose({
    loadStatus,
    isLoading
})
</script>
