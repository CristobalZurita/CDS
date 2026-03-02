<template>
    <div class="foxy-item-faq-question">
        <!-- Question Icon -->
        <div class="flex-shrink-0">
            <i class="fa fa-question-circle text-primary question-icon eq-h4"/>
        </div>

        <!-- Question Content -->
        <div class="foxy-item-faq-question-content">
            <h5 class="foxy-item-faq-question-title lead-2"
                v-html="parsedQuestion"/>

            <p class="foxy-item-faq-question-answer text-4 text-light-7"
               v-html="parsedAnswer"/>
        </div>
    </div>
</template>

<script setup>
import {computed} from "vue"
import {useUtils} from "/src/composables/utils.js"

const utils = useUtils()

const props = defineProps({
    question: String,
    answer: String
})

const parsedQuestion = computed(() => {
    return utils.parseCustomText(props.question)
})

const parsedAnswer = computed(() => {
    return utils.parseCustomText(props.answer)
})
</script>
