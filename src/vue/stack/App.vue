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
import StateProviderLayer from "@/vue/stack/StateProviderLayer.vue"
import FeedbacksLayer from "@/vue/stack/FeedbacksLayer.vue"
import ContentLayer from '@/vue/stack/ContentLayer.vue'
import FloatingQuoteButton from "@/vue/components/widgets/FloatingQuoteButton.vue"
import {useEmails} from "@/composables/emails.js"
import {onMounted} from "vue"

const emails = useEmails()

onMounted(() => {
    emails.init()
})
</script>

<style lang="scss" scoped>
</style>