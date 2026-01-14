<template>
    <form id="foxy-contact-form" @submit="_onFormSubmit">
        <ContactFormFields v-if="shouldDisplayFormFields"
                           :error-message="errorMessage"
                           @input="_onInput"/>

        <ContactFormSuccess v-else
                            :email="email"/>
    </form>
</template>

<script setup>
import {computed, inject, onMounted, provide, ref, watch} from "vue"
import {useStrings} from "/src/composables/strings.js"
import {useLayout} from "/src/composables/layout.js"
import {useEmails} from "/src/composables/emails.js"
import {useUtils} from "/src/composables/utils.js"

import ContactFormFields from "/src/vue/components/forms/contact/ContactFormFields.vue"
import ContactFormSuccess from "/src/vue/components/forms/contact/ContactFormSuccess.vue"

const layout = useLayout()
const strings = useStrings()
const emails = useEmails()
const utils = useUtils()
const setSpinnerEnabled = inject("setSpinnerEnabled")

const name = ref("")
const email = ref("")
const subject = ref("")
const message = ref("")
const apiResponse = ref(null)
const validationError = ref(null)

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

    const success = await emails.sendContact(name.value, email.value, subject.value, message.value)
    apiResponse.value = {success: success}

    _resetScroll()
    setSpinnerEnabled && setSpinnerEnabled(false)
}

const _resetScroll = () => {
    const element = document.getElementById('contact') || document.getElementById('foxy-contact-form')
    layout.scrollIntoView(element)
}
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

#foxy-contact-form {
    width: 100%;
    @include media-breakpoint-down(lg) {
        max-width: 680px;
        margin: 0 auto;
    }
}
</style>