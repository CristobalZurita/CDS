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

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

div.foxy-contact-form-row {
    --column-spacing: 12px;
    @include media-breakpoint-down(lg) {
        --column-spacing: 8px;
    }

    div.foxy-contact-form-alert-column {
        padding-bottom: calc(var(--column-spacing) * 1.5);
        @include media-breakpoint-down(lg) {
            padding-bottom: var(--column-spacing);
        }
    }

    div.foxy-contact-form-left-column {
        padding-right: calc(var(--column-spacing)/2);
        padding-bottom: calc(var(--column-spacing) * 3);
        @include media-breakpoint-down(lg) {
            padding-right: 0;
            padding-bottom: var(--column-spacing);
        }
    }

    div.foxy-contact-form-right-column {
        padding-left: var(--column-spacing);
        padding-bottom: calc(var(--column-spacing) * 3);
        @include media-breakpoint-down(lg) {
            padding-left: 0;
            padding-bottom: calc(var(--column-spacing) * 3);
        }
    }

    div.input-group {
        &:not(:last-child) {
            padding-bottom: calc(var(--column-spacing));
        }
    }
}

/** ----------- FORM SIZES AND LAYOUT ------------- **/
span.input-group-attach {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    min-width: 70px;
    @include media-breakpoint-down(xl) {
        font-size: 1rem;
        width: 65px;
    }
    @include media-breakpoint-down(sm) {
        min-width: 50px;
        font-size: 0.9rem;
    }
}

input, textarea {
    font-size: 1rem;
    padding: 1rem;
    @include media-breakpoint-down(lg) {
        font-size: 0.9rem;
        padding: 0.9rem;
    }
    @include media-breakpoint-down(sm) {
        font-size: 0.85rem;
        padding: 0.85rem;
    }
}

input {
    height: 70px;
    @include media-breakpoint-down(lg) {
        height: 60px;
    }
    @include media-breakpoint-down(sm) {
        height: 50px;
    }
}

div.form-group-textarea {
    height: 100%;
}

textarea {
    height: 100%;
    flex-grow: 1;
    min-height: 200px;
    @include media-breakpoint-down(sm) {
        min-height: 150px;
    }
}

/** ----------- FORM COLORS ------------- **/
input, textarea {
    background-color: lighten($dark, 5%);
    border-color: lighten($dark, 12%);
    border-width: 2px;
    color: $white;
    transition: 0.1s border-color ease-in-out;

    &:focus {
        background-color: $dark;
        border-color: $primary;
        color: $white;
        box-shadow: none;
    }
}

span.input-group-attach {
    background-color: lighten($dark, 1%);
    border-color: lighten($dark, 15%);
    color: $light-5;
    border-width: 2px;
    border-right-width: 0;
    transition: 0.1s background-color ease-in-out, 0.1s border-color ease-in-out;
}

input {
    &:-webkit-autofill,
    &:-webkit-autofill:hover,
    &:-webkit-autofill:focus,
    &:-webkit-autofill:active{
        -webkit-box-shadow: 0 0 0 2px lighten($dark, 1%) inset !important;
        -webkit-text-fill-color: $light !important;
        color: $light!important;
        transition: background-color 5000s ease-in-out 0s;
    }

    &:-webkit-autofill:focus {
        border-color: $primary;
    }
}

div.form-group-focused {
    span.input-group-attach {
        background-color: lighten($primary, 6%);
        border-color: $primary;
        color: $light-1;
    }
}

/** ----------- PLACEHOLDERS ------------- **/
$input-placeholder-text-color: darken($light-6, 7%);

::-webkit-input-placeholder {
    --font-size: 1rem;
    @include media-breakpoint-down(lg) {
        --font-size: 0.9rem;
    }

    font-size: var(--font-size);
    color: $input-placeholder-text-color;
}

*:-moz-placeholder {
    /* FF 4-18 */
    color: $input-placeholder-text-color!important;
    opacity: 1;
}
*::-moz-placeholder {
    /* FF 19+ */
    color: $input-placeholder-text-color!important;
    opacity: 1;
}
*:-ms-input-placeholder {
    /* IE 10+ */
    color: $input-placeholder-text-color!important;
}
*::-ms-input-placeholder {
    /* Microsoft Edge */
    color: $input-placeholder-text-color!important;
}
*::placeholder {
    /* modern browser */
    color: $input-placeholder-text-color!important;
}
</style>