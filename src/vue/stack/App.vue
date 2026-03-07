<template>
    <div id="app-root" class="app-container">
        <router-view />
        <ToastNotification ref="toastComponent" />
        <StoreCartWidget />
    </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { useAuthStore } from "@/stores/auth"
import { initAnalytics, track } from "@/analytics"
import { AnalyticsEvents } from "@/analytics/events"
import ToastNotification from "@/vue/components/system/ToastNotification.vue"
import StoreCartWidget from "@/vue/components/widgets/StoreCartWidget.vue"
import { setToastComponent } from "@/services/toastService"

const _auth = useAuthStore()
const toastComponent = ref(null)

onMounted(() => {
    if (toastComponent.value) {
        setToastComponent(toastComponent.value)
    }
    initAnalytics()
    track(AnalyticsEvents.PAGE_VIEW, {
        page: window.location.pathname,
    })
})
</script>
