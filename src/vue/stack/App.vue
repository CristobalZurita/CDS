<template>
    <div id="app-root" class="app-container">
        <router-view />
    </div>
</template>

<script setup>
import { onMounted } from "vue"
import { useAuthStore } from "@/stores/auth"
import { initAnalytics, track } from "@/analytics"
import { AnalyticsEvents } from "@/analytics/events"

const auth = useAuthStore()

onMounted(() => {
    initAnalytics()
    track(AnalyticsEvents.PAGE_VIEW, {
        page: window.location.pathname,
    })
})
</script>

<style scoped lang="scss">
#app-root {
    min-height: 100vh;
}
</style>
