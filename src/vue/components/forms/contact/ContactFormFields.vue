<template>
    <div class="foxy-contact-form-row row g-0">
        <!-- Error Alert Alert -->
        <div v-if="errorMessage"
             class="foxy-contact-form-alert-column col-12">
            <Alert variant="danger"
                   :message="errorMessage"/>
        </div>

        <!-- Left Column -->
        <div class="foxy-contact-form-left-column col-lg-6">
            <!-- Input Groups -->
            <div v-for="item in inputItems"
                 class="form-group input-group"
                 :class="focusId === item.id ? `form-group-focused` : ``">
                <!-- Icon Attach -->
                <span class="input-group-text input-group-attach">
                    <i :class="item.faIcon"/>
                </span>

                <!-- Input -->
                <input class="form-control"
                       :data-testid="`contact-${item.id}`"
                       :id="`form-${item.id}`"
                       :type="item.type"
                       :name="item.id"
                       :placeholder="`${strings.get(item.id)} *`"
                       @input="_onInputChanged"
                       @focusin="_onFocusIn(item.id)"
                       @focusout="_onFocusOut(item.id)"
                       required/>
            </div>
        </div>


        <!-- Right Column -->
        <div class="foxy-contact-form-right-column col-lg-6">
            <!-- Textarea -->
            <div class="form-group form-group-textarea mb-md-0">
                <textarea class="form-control"
                          data-testid="contact-message"
                          id="form-message"
                          placeholder="Message *"
                          maxlength="2048"
                          @input="_onInputChanged"
                          @focusin="_onFocusIn('message')"
                          @focusout="_onFocusOut('message')"
                          required/>
            </div>
        </div>

        <!-- Buttons -->
        <div class="foxy-contact-form-bottom-column col-lg-12 text-center">
            <XLButton :label="strings.get('send')"
                      class="btn-submit btn-primary-light"
                      type="submit"
                      icon="fa-solid fa-envelope"/>
        </div>
    </div>
</template>

<script setup>
import Alert from "/src/vue/components/widgets/Alert.vue"
import XLButton from "/src/vue/components/widgets/XLButton.vue"
import {inject, ref} from "vue"
import {useStrings} from "/src/composables/strings.js"

const strings = useStrings()

const props = defineProps({
    errorMessage: String,
})

const emit = defineEmits(["input"])

const focusId = ref(null)

const inputItems = [
    {id: 'name', faIcon: 'fa-solid fa-signature', type: 'text'},
    {id: 'email', faIcon: 'fa-solid fa-envelope', type: 'email'},
    {id: 'subject', faIcon: 'fa-solid fa-pen-to-square', type: 'text'},
]

const _onFocusIn = (id) => {
    focusId.value = id
}

const _onFocusOut = (id) => {
    focusId.value = null
}

const _onInputChanged = (e) => {
    const target = e.target
    emit("input", target.id.replace("form-" , ""), target.value)
}
</script>
