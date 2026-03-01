<template>
    <form id="foxy-contact-form" data-testid="contact-form" @submit="_onFormSubmit">
        <ContactFormFields v-if="shouldDisplayFormFields"
                           :error-message="errorMessage"
                           @input="_onInput"/>

        <TurnstileWidget v-if="shouldDisplayFormFields" @verify="onVerify" />

        <ContactFormSuccess v-else
                            :email="email"/>
    </form>
</template>

<script setup>
import {computed, inject, onMounted, provide, ref, watch} from "vue"
import {track} from "@/analytics"
import {AnalyticsEvents} from "@/analytics/events"
import {useStrings} from "/src/composables/strings.js"
import {useLayout} from "/src/composables/layout.js"
import {useEmails} from "/src/composables/emails.js"
import {useApi} from "/src/composables/useApi.js"
import {useUtils} from "/src/composables/utils.js"

import ContactFormFields from "/src/vue/components/forms/contact/ContactFormFields.vue"
import ContactFormSuccess from "/src/vue/components/forms/contact/ContactFormSuccess.vue"
import TurnstileWidget from "@/vue/components/widgets/TurnstileWidget.vue"

const layout = useLayout()
const strings = useStrings()
const emails = useEmails()
const api = useApi()
const utils = useUtils()
const setSpinnerEnabled = inject("setSpinnerEnabled")

const name = ref("")
const email = ref("")
const subject = ref("")
const message = ref("")
const apiResponse = ref(null)
const validationError = ref(null)
const turnstileToken = ref("")

const shouldDisplayFormFields = computed(() => {
    return !apiResponse.value || !apiResponse.value.success
})

const errorMessage = computed(() => {
    if(apiResponse.value && !apiResponse.value.success)
        return strings.get("error_sending_message")

    if(validationError.value)
        return strings.get(validationError.value)
    return null
})

const _onInput = (field, value) => {
    switch (field) {
        case "name": name.value = value; break
        case "email": email.value = value; break
        case "subject": subject.value = value; break
        case "message": message.value = value; break
    }
}

const _onFormSubmit = async (e) => {
    e.preventDefault && e.preventDefault()

    _validate()
    if(validationError.value) {
        track(AnalyticsEvents.CONTACT_VALIDATION_ERROR, {field: validationError.value}, {page: utils.getAbsoluteLocation()})
        _resetScroll()
        return
    }
    if(!turnstileToken.value) {
        validationError.value = "error_fill_all_fields"
        _resetScroll()
        return
    }

    _submit().then(r => {})
}

const _validate = () => {
    validationError.value = null
    if(!name.value.length || !email.value.length || !subject.value.length || !message.value.length) {
        validationError.value = "error_fill_all_fields"
    }
    if(!utils.isValidEmail(email.value)) {
        validationError.value = "error_invalid_email"
    }
}

const _submit = async () => {
    setSpinnerEnabled && setSpinnerEnabled(true, strings.get('sending_message'))

    const [emailResult, apiResult] = await Promise.allSettled([
        emails.sendContact(name.value, email.value, subject.value, message.value),
        _submitToApi()
    ])

    const emailOk = emailResult.status === "fulfilled" && emailResult.value === true
    const apiOk = apiResult.status === "fulfilled" && apiResult.value === true

    apiResponse.value = {success: emailOk || apiOk}
    if(apiResponse.value.success) {
        track(AnalyticsEvents.CONTACT_SUBMIT_SUCCESS, {source: 'contact_form'}, {page: utils.getAbsoluteLocation()})
    } else {
        track(AnalyticsEvents.CONTACT_SUBMIT_ERROR, {source: 'contact_form'}, {page: utils.getAbsoluteLocation()})
    }

    _resetScroll()
    setSpinnerEnabled && setSpinnerEnabled(false)
}

const _submitToApi = async () => {
    try {
        await api.post("/contact/", {
            name: name.value,
            email: email.value,
            subject: subject.value,
            message: message.value,
            source_url: utils.getAbsoluteLocation(),
            turnstile_token: turnstileToken.value
        })
        return true
    } catch (error) {
        return false
    }
}

const onVerify = (token) => {
    turnstileToken.value = token
}

const _resetScroll = () => {
    const element = document.getElementById('contact') || document.getElementById('foxy-contact-form')
    layout.scrollIntoView(element)
}
</script>

<style lang="scss" scoped>
@import "@/scss/_theming.scss";

#foxy-contact-form {
    width: 100%;
    @include media-breakpoint-down(lg) {
        max-width: 680px;
        margin: 0 auto;
    }
}
</style>
