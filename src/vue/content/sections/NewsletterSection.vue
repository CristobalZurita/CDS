<template>
    <PageSection variant="default"
                 :id="props.id">
        <PageSectionHeader title="*Newsletter*"
                           subtitle="Recibe novedades, talleres y anuncios importantes"/>

        <PageSectionContent>
            <form class="newsletter-form" @submit="onSubmit">
                <div class="newsletter-input-group">
                    <input
                        v-model.trim="email"
                        data-testid="newsletter-email"
                        class="newsletter-input"
                        type="email"
                        name="newsletter-email"
                        placeholder="Tu correo electrónico"
                        required
                    />
                    <XLButton
                        class="newsletter-button"
                        label="Suscribirme"
                        type="submit"
                        icon="fa-solid fa-paper-plane"
                    />
                </div>

                <TurnstileWidget @verify="onVerify" />

                <p v-if="statusMessage"
                   data-testid="newsletter-status"
                   class="newsletter-status"
                   :class="statusClass">
                    {{ statusMessage }}
                </p>
            </form>
        </PageSectionContent>
    </PageSection>
</template>

<script setup>
import { computed, ref } from "vue"
import { track } from "@/analytics"
import { AnalyticsEvents } from "@/analytics/events"
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionHeader from "/src/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"
import XLButton from "/src/vue/components/widgets/XLButton.vue"
import TurnstileWidget from "@/vue/components/widgets/TurnstileWidget.vue"
import { useApi } from "/src/composables/useApi.js"
import { useUtils } from "/src/composables/utils.js"

const props = defineProps({
    id: String
})

const api = useApi()
const utils = useUtils()

const email = ref("")
const status = ref("idle")
const statusMessage = ref("")
const turnstileToken = ref("")

const statusClass = computed(() => {
    return status.value === "success" ? "is-success" : "is-error"
})

const onSubmit = async (event) => {
    event.preventDefault()
    status.value = "idle"
    statusMessage.value = ""
    if (!turnstileToken.value) {
        status.value = "error"
        statusMessage.value = "Completa el captcha antes de continuar."
        return
    }

    try {
        await api.post("/newsletter/subscribe", {
            email: email.value,
            source_url: utils.getAbsoluteLocation(),
            turnstile_token: turnstileToken.value
        })
        status.value = "success"
        statusMessage.value = "Gracias por suscribirte. Te avisaremos de nuevas novedades."
        track(AnalyticsEvents.NEWSLETTER_SUBMIT_SUCCESS, { source: 'newsletter_section' }, { page: utils.getAbsoluteLocation() })
        email.value = ""
    } catch (error) {
        status.value = "error"
        statusMessage.value = "No pudimos registrar tu suscripción. Intenta nuevamente."
        track(AnalyticsEvents.NEWSLETTER_SUBMIT_ERROR, { source: 'newsletter_section' }, { page: utils.getAbsoluteLocation() })
    }
}

const onVerify = (token) => {
    turnstileToken.value = token
}
</script>

<style lang="scss" scoped>
@use '@/scss/theming' as *;

.newsletter-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.newsletter-input-group {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    align-items: stretch;
}

.newsletter-input {
    flex: 1 1 320px;
    border-radius: 999px;
    border: 1px solid rgba($color-black, 0.12);
    padding: 0.95rem 1.4rem;
    font-size: 1rem;
    color: $text-normal;
    background: $white;
}

.newsletter-button {
    white-space: nowrap;
}

.newsletter-status {
    margin: 0;
    font-weight: 600;
    font-size: 0.98rem;
}

.newsletter-status.is-success {
    color: $success;
}

.newsletter-status.is-error {
    color: $danger;
}

@media (max-width: 640px) {
    .newsletter-input-group {
        flex-direction: column;
    }

    .newsletter-button {
        width: 100%;
        justify-content: center;
    }
}
</style>
