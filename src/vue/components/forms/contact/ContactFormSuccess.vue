<template>
    <div class="foxy-contact-form-success" data-testid="contact-success">
        <div class="foxy-contact-form-success-icon-wrapper display-3">
            <i class="fa-solid fa-envelope-circle-check"/>
        </div>

        <div class="foxy-contact-form-success-content-wrapper mt-2">
            <h3 v-html="utils.parseCustomText(strings.get('contact_thank_you'), true)"/>

            <p class="text-4 mt-4 mb-3"
               v-html="utils.parseCustomText(strings.get('contact_thank_you_description'))"/>

            <p class="text-4"
               data-testid="contact-success-email"
               v-html="utils.parseCustomText(strings.get('contact_thank_you_reply').replaceAll('{email}', props.email), true)"/>
        </div>
    </div>
</template>

<script setup>
import {useStrings} from "/src/composables/strings.js"
import {useUtils} from "/src/composables/utils.js"

const strings = useStrings()
const utils = useUtils()

const props = defineProps({
    email:String
})
</script>
