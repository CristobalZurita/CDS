<template>
    <div class="foxy-contact-form-success">
        <div class="foxy-contact-form-success-icon-wrapper display-3">
            <i class="fa-solid fa-envelope-circle-check"/>
        </div>

        <div class="foxy-contact-form-success-content-wrapper mt-2">
            <h3 v-html="utils.parseCustomText(strings.get('contact_thank_you'), true)"/>

            <p class="text-4 mt-4 mb-3"
               v-html="utils.parseCustomText(strings.get('contact_thank_you_description'))"/>

            <p class="text-4"
               v-html="utils.parseCustomText(strings.get('contact_thank_you_reply').replaceAll('{email}', props.email), true)"/>
        </div>
    </div>
</template>

<script setup>
import {useStrings} from "/src/composables/strings.js"
import {useUtils} from "/src/composables/utils.js"
import Divider from "/src/vue/components/widgets/Divider.vue"

const strings = useStrings()
const utils = useUtils()

const props = defineProps({
    email:String
})
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

div.foxy-contact-form-success {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    background-color: rgba($dark, 0.05);
    border: 1px dashed rgba(black, 0.2);
    padding: 40px 30px;
    border-radius: 10px;
}

div.foxy-contact-form-success-content-wrapper {
    text-align: center;

    h3 {
        color: $light-3;
        font-family: $font-family-base;
        font-weight: bold;
    }

    p {
        color: $light-5;
    }
}
</style>