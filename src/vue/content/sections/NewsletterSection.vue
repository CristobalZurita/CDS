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

                <p v-if="statusMessage"
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
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionHeader from "/src/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"
import XLButton from "/src/vue/components/widgets/XLButton.vue"
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

const statusClass = computed(() => {
    return status.value === "success" ? "is-success" : "is-error"
})

const onSubmit = async (event) => {
    event.preventDefault()
    status.value = "idle"
    statusMessage.value = ""

    try {
        await api.post("/newsletter/subscribe", {
            email: email.value,
            source_url: utils.getAbsoluteLocation()
        })
        status.value = "success"
        statusMessage.value = "Gracias por suscribirte. Te avisaremos de nuevas novedades."
        email.value = ""
    } catch (error) {
        status.value = "error"
        statusMessage.value = "No pudimos registrar tu suscripción. Intenta nuevamente."
    }
}
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

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
    border: 1px solid rgba(0, 0, 0, 0.12);
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
