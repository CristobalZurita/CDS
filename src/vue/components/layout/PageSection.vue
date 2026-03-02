<template>
    <!-- Site Section -->
    <section ref="sectionRef"
             class="foxy-section"
             :id="id"
             :data-zone="id"
             :class="classList">

        <BackgroundPromo v-if="props.variant === 'promo'"
                         :faded="true"/>

        <!-- Container -->
        <div class="container-xxl">
            <header v-if="$slots.header">
                <slot name="header" />
            </header>

            <div class="section-content">
                <slot />
            </div>

            <footer v-if="$slots.footer">
                <slot name="footer" />
            </footer>
        </div>
    </section>
</template>

<script setup>
import {computed, onBeforeUnmount, onMounted, ref} from "vue"
import { track } from "@/analytics"
import { AnalyticsEvents } from "@/analytics/events"
import BackgroundPromo from "/src/vue/components/layout/BackgroundPromo.vue"

const props = defineProps({
    id: String,
    variant: String, // default, primary, dark or promo.
    name: String,
    faIcon: String
})

const classList = computed(() => {
    return props.variant ?
        `foxy-section-${props.variant}` :
        ``
})

const sectionRef = ref(null)
let observer = null

onMounted(() => {
    if (!sectionRef.value) return
    observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible')
                track(AnalyticsEvents.SECTION_FOCUS, null, {
                    page: window.location.pathname,
                    section: props.id || 'unknown'
                })
            }
        })
    }, { threshold: 0.35 })
    observer.observe(sectionRef.value)
})

onBeforeUnmount(() => {
    if (observer && sectionRef.value) {
        observer.unobserve(sectionRef.value)
    }
    observer = null
})
</script>
