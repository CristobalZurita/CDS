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
                        <a class="btn-hero btn-hero-primary">
                            <i class="fa-solid fa-file-circle-check"></i>
                            <span>Cotiza tu instrumento</span>
                        </a>
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

const utils = useUtils()
const showAppointmentModal = ref(false)

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
}

const handleAppointmentSubmit = async (formData) => {
    // Enviar a backend
    try {
        const response = await fetch('/api/v1/appointments/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        
        if (response.ok) {
            console.log('Cita agendada exitosamente')
        }
    } catch (error) {
        console.error('Error al agendar cita:', error)
    }
}
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

header.foxy-header {
    /* expanded hero height to match reference - black box extends lower for buttons */
   --height: clamp(600px, 90vh, 1100px);
    --content-margin-top: 64px;
    --max-logo-proportion:45vw;
    --max-logo-height:60vh; /* allow much taller hero on large viewports */
    @include media-breakpoint-down(xl) {--max-logo-height: 45vh;}
    @include media-breakpoint-down(lg) {--max-logo-height: 38vh; }
    @include media-breakpoint-down(md) {--content-margin-top: 65px;}

    --content-height: calc(var(--height) - var(--content-margin-top));
    --logo-proportion: clamp(190px, 45vw, min(37.5vh, 35vw, 350px));

    position: relative;
    height: var(--height);

    div.container-xxl {
        display: flex;
        align-items: center;
        justify-content: center;

        /* allow the hero container to span wide viewports without being overly constrained */
        max-width: 1400px;
        width: 100%;
        height: var(--height);
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 2rem;
    }

    article.foxy-hero-header {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        padding-top: calc(var(--content-margin-top));
          
        position: relative;
        z-index: 3;
    }

    div.foxy-hero-header-logo {
        /* allow rectangular logos on desktop while keeping a sensible max height */
        width: clamp(750px, 96vw, 1700px); /* make the banner start wider on large screens */
        max-width: 98%;
        /* Fix hero to a landscape presentation on desktop by using a fixed display height
           and covering the area. This crops tall uploads to appear apaisado as requested. */
        height: min(50vh, 420px);
        max-height: var(--max-logo-height);
        margin: 0 auto;

        img.image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }
    }

    h1.heading {
        color:$orange-pastel;
        text-transform: uppercase;
        text-align: center;
        font-family: 'Cervo Neue', 'Steelfish', sans-serif;
        font-weight: 800;
        font-size: clamp(60px, 7vw, 10px);
           transform: scale(2);            /* agranda visualmente */
    transform-origin: center top;
        padding: 1.5rem 0 1.95rem;
        letter-spacing: 0.08em;
        line-height: 0.5;
        position: relative;
        z-index: 5;
        margin: 0;
    }

    h4.subheading {
        font-family: 'Cervo Neue', $font-family-base;
        color: $light-5;
        font-weight: 400;
        font-size: clamp(16px, calc(var(--logo-proportion)/14), 100px);
        padding: calc(var(--logo-proportion)/20) 0;
        line-height: 24px;
        text-align: center;
    }

    .hero-cta-buttons {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2.5rem;
        margin-top: 2.5rem;
        position: relative;
        z-index: 6; /* Ensure CTAs sit above decorative background */

        @include media-breakpoint-down(md) {
            gap: 1.2rem;
            flex-wrap: wrap;
        }
    }

    .btn-hero {
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1.25rem 2.8rem;
        border-radius: 4rem;
        border: 2px solid $orange-pastel;
        background-color: $orange-pastel;
        color: white;
        font-family: 'Cervo Neue', $headings-font-family;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 1.25rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        letter-spacing: 0.05em;

        i {
            font-size: 1.3rem;
        }

        &:hover {
            background-color: #ff7f1f;
            border-color: #ff7f1f;
            color: white;
            transform: scale(1.08);
        }

        &:active {
            transform: scale(0.98);
        }

        &.btn-hero-primary {
            background-color: $orange-pastel;
            color: white;
            border-color: $orange-pastel;

            &:hover {
                background-color: #ff7f1f;
                border-color: #ff7f1f;
            }
        }
    }
}
</style>