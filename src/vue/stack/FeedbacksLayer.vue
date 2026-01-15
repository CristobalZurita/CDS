<template>
    <ActivitySpinner :visible="Boolean(spinnerActive)"
                     :message="String(spinnerMessage)"/>

    <Loader v-if="loaderEnabled"
            :visible="Boolean(loaderActive)"
            :refresh-count="Number(loaderPageRefreshCount)"
            :smooth-transition-enabled="Boolean(loaderSmoothTransitionEnabled)"
            @rendered="_onLoaderRendered"
            @ready="_onLoaderReady"
            @leaving="_onLoaderWillLeave"
            @completed="_onLoaderCompleted"/>

    <slot v-if="isReady" :floatingButtonVisible="floatingButtonVisible"/>
</template>

<script setup>
import {inject, ref, onMounted, onUnmounted} from "vue"
import ActivitySpinner from "/src/vue/components/loaders/ActivitySpinner.vue"
import Loader from "/src/vue/components/loaders/Loader.vue"

const loaderEnabled = inject("loaderEnabled")
const LoaderAnimationStatus = inject("LoaderAnimationStatus")
const loaderActive = inject("loaderActive")
const loaderPageRefreshCount = inject("loaderPageRefreshCount")
const loaderSmoothTransitionEnabled = inject("loaderSmoothTransitionEnabled")
const loaderAnimationStatus = inject("loaderAnimationStatus")
const spinnerActive = inject("spinnerActive")
const spinnerMessage = inject("spinnerMessage")
const floatingButtonVisible = inject("floatingButtonVisible")
const hasUserInteracted = inject("hasUserInteracted")

const isReady = ref(!loaderEnabled)

if (loaderEnabled) {
  loaderAnimationStatus.value = LoaderAnimationStatus.INITIALIZED
}

// Detectar primera interacción del usuario (scroll, click, navegación)
const _onUserInteraction = () => {
  if (!hasUserInteracted.value) {
    hasUserInteracted.value = true
    floatingButtonVisible.value = true
    // Remover listeners después de detectar primera interacción
    document.removeEventListener('scroll', _onUserInteraction)
    document.removeEventListener('click', _onUserInteraction)
    window.removeEventListener('hashchange', _onUserInteraction)
  }
}

const _onLoaderRendered = () => {
    loaderAnimationStatus.value = LoaderAnimationStatus.RENDERED
}

const _onLoaderReady = () => {
    isReady.value = true
    loaderAnimationStatus.value = LoaderAnimationStatus.TRACKING_PROGRESS
    
    // Agregar listeners para detectar interacción después de que el loader esté listo
    document.addEventListener('scroll', _onUserInteraction)
    document.addEventListener('click', _onUserInteraction)
    window.addEventListener('hashchange', _onUserInteraction)
}

const _onLoaderWillLeave = () => {
    loaderAnimationStatus.value = LoaderAnimationStatus.LEAVING
}

const _onLoaderCompleted = () => {
    loaderActive.value = false
}

// Cleanup
onUnmounted(() => {
  document.removeEventListener('scroll', _onUserInteraction)
  document.removeEventListener('click', _onUserInteraction)
  window.removeEventListener('hashchange', _onUserInteraction)
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
</style>