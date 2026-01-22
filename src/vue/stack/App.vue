<template>
    <StateProviderLayer>
        <FeedbacksLayer>
            <ContentLayer>
                <!-- Let the router mount the layout (Master) and its children -->
                <router-view />
            </ContentLayer>
        </FeedbacksLayer>
    </StateProviderLayer>

    <FloatingQuoteButton />
</template>

<script setup>
import StateProviderLayer from "/src/vue/stack/StateProviderLayer.vue"
import FeedbacksLayer from "/src/vue/stack/FeedbacksLayer.vue"
import ContentLayer from "/src/vue/stack/ContentLayer.vue"
import FloatingQuoteButton from "/src/vue/components/widgets/FloatingQuoteButton.vue"
import {useEmails} from "/src/composables/emails.js"
import {onMounted} from "vue"
import { initAnalytics, setAnalyticsContext, track } from '@/analytics'
import { AnalyticsEvents } from '@/analytics/events'

const emails = useEmails()

onMounted(() => {
    emails.init()
    initAnalytics()
    setAnalyticsContext({ page: window.location.pathname })

    const firedDepths = new Set()
    const depthMap = [
        { threshold: 0.25, event: AnalyticsEvents.SCROLL_DEPTH_25 },
        { threshold: 0.5, event: AnalyticsEvents.SCROLL_DEPTH_50 },
        { threshold: 0.75, event: AnalyticsEvents.SCROLL_DEPTH_75 },
        { threshold: 0.98, event: AnalyticsEvents.SCROLL_DEPTH_100 }
    ]

    const onScroll = () => {
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight
        if (scrollHeight <= 0) return
        const progress = window.scrollY / scrollHeight
        depthMap.forEach(({ threshold, event }) => {
            if (progress >= threshold && !firedDepths.has(event)) {
                firedDepths.add(event)
                track(event, null, { page: window.location.pathname })
            }
        })
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
})
</script>

<style lang="scss" scoped>
</style>
