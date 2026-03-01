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

<style lang="scss">
@use '@/scss/theming' as *;

section.foxy-section {
    opacity: 0;
    transform: translateY(16px);
    transition: opacity 0.6s ease, transform 0.6s ease;

    &.is-visible {
        opacity: 1;
        transform: translateY(0);
    }

    @include generate-dynamic-styles-with-hash((
        xxxl: (padding: 5rem 0em 5.5rem),  // Increased for large screens
        xxl:  (padding: 4rem 0rem 4.5rem),  // Increased for consistency
        lg:   (padding: 3rem 0rem 3.5rem),  // Laptop
        md:   (padding: 3rem 0rem 3.5rem),  // Tablet portrait - INCREASED from 2.25/3.25
        sm:   (padding: 2.5rem 0rem 3rem),  // Mobile - INCREASED from 2/3
    ));

    background-color: $background-color;
    position: relative;

    .section-content {
        /* Allow full-width section content for grid/columns -- keep readable class for long-form text */
        max-width: 1200px;
        width: 100%;
        margin-left: auto;
        margin-right: auto;

        /* Use .readable on text-only blocks to limit to optimal line length */
        &.readable {
            max-width: 75ch;
        }
    }

    .foxy-promo-background {
        display: block;
        margin-top: -4rem;
    }
}

section.foxy-section-primary {
    background-color: lighten($primary, 42%);
}

section.foxy-section-dark {
    background-color: lighten($dark, 10%);
    color: $text-normal-contrast;

    h5.foxy-section-header-subtitle {
        color: $light-5;
    }
}

section.foxy-section-promo {
    background-color: transparent;
}


</style>
