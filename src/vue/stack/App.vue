<template>
    <StateProviderLayer>
        <FeedbacksLayer>
            <ContentLayer>
                <!-- Let the router mount the layout (Master) and its children -->
                <router-view />
            </ContentLayer>
        </FeedbacksLayer>
    </StateProviderLayer>

    <!-- Botón flotante global -->
    <FloatingQuoteButton />
</template>

<script setup>
import StateProviderLayer from "/src/vue/stack/StateProviderLayer.vue"
import FeedbacksLayer from "/src/vue/stack/FeedbacksLayer.vue"
import ContentLayer from "/src/vue/stack/ContentLayer.vue"
import FloatingQuoteButton from "/src/vue/components/widgets/FloatingQuoteButton.vue"
import {useEmails} from "/src/composables/emails.js"
import {onMounted} from "vue"

const emails = useEmails()

onMounted(() => {
    emails.init()
})
</script>

<style lang="scss" scoped>
</style>