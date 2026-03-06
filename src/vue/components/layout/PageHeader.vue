<template>
    <header :id="id"
            class="foxy-header">
        <BackgroundPromo :faded="false"/>

        <!-- Content -->
        <div class="container-xxl">
            <article class="foxy-hero-header">
                <!-- Logo -->
                <ImageView :src="logoUrl"
                           :spinner-enabled="true"
                           :alt="title"
                           class="foxy-hero-header-logo"/>

                <!-- Texts -->
                <h1 class="heading"
                    v-html="parsedTitle"/>
                <h4 class="subheading"
                    v-html="parsedSubtitle"/>

                <!-- CTA Buttons -->
                <div v-if="showCtaButtons" class="hero-cta-buttons">
                    <button class="btn-hero" @click="openAppointmentModal">
                        <i class="fa-solid fa-calendar"></i>
                        <span>Agenda tu hora</span>
                    </button>
                    <Link url="/cotizador-ia">
                        <span class="btn-hero btn-hero-primary" role="link" tabindex="0" @click="handleQuoteClick">
                            <i class="fa-solid fa-file-circle-check"></i>
                            <span>Cotiza tu instrumento</span>
                        </span>
                    </Link>
                    <Link v-if="!isAuthenticated" url="/login">
                        <span class="btn-hero btn-hero-outline" role="link" tabindex="0" @click="handleLoginClick">
                            <i class="fa-solid fa-right-to-bracket"></i>
                            <span>Iniciar sesión</span>
                        </span>
                    </Link>
                </div>

                <!-- Appointment Modal -->
                <AppointmentModal v-if="showAppointmentModal" 
                                  @close="showAppointmentModal = false"
                                  @submit="handleAppointmentSubmit"/>


                <!-- Button -->
                <Link v-if="showButton"
                      :url="props.buttonUrl">
                    <XLButton :label="buttonLabel"
                              :icon="buttonIcon"
                              :class="`mt-4`"/>
                </Link>
            </article>
        </div>
    </header>
</template>

<script setup>
import BackgroundPromo from "/src/vue/components/layout/BackgroundPromo.vue"
import ImageView from "/src/vue/components/generic/ImageView.vue"
import {useUtils} from "/src/composables/utils.js"
import {computed, ref} from "vue"
import Link from "/src/vue/components/generic/Link.vue"
import XLButton from "/src/vue/components/widgets/XLButton.vue"
import AppointmentModal from "/src/vue/components/modals/AppointmentModal.vue"
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'
import { track } from '@/analytics'
import { AnalyticsEvents } from '@/analytics/events'

const utils = useUtils()
const showAppointmentModal = ref(false)
const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const props = defineProps({
    id: String,
    title: String,
    subtitle: String,
    logoUrl: String,
    showButton: Boolean,
    showCtaButtons: Boolean,
    buttonLabel: String,
    buttonIcon: String,
    buttonUrl: String
})

const parsedTitle = computed(() => {
    return utils.parseCustomText(props.title)
})

const parsedSubtitle = computed(() => {
    return utils.parseCustomText(props.subtitle)
})

const openAppointmentModal = () => {
    showAppointmentModal.value = true
    track(AnalyticsEvents.HERO_CTA_APPOINTMENT, null, { page: window.location.pathname })
}

const handleQuoteClick = () => {
    track(AnalyticsEvents.HERO_CTA_QUOTE, null, { page: window.location.pathname })
}

const handleLoginClick = () => {
    track(AnalyticsEvents.HERO_CTA_LOGIN, null, { page: window.location.pathname })
}

const handleAppointmentSubmit = async (formData) => {
    // Enviar a backend
    try {
        await api.post('/appointments/', formData)
        track(AnalyticsEvents.APPOINTMENT_SUBMIT_SUCCESS, { source: 'hero' }, { page: window.location.pathname })
    } catch (error) {
        console.error('Error al agendar cita:', error)
        track(AnalyticsEvents.APPOINTMENT_SUBMIT_ERROR, { source: 'hero' }, { page: window.location.pathname })
    }
}
</script>
