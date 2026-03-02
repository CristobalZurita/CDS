<template>
    <div class="foxy-section-footer">
        <div class="row">
            <div class="foxy-section-footer-content col-12 col-lg-8">
                <Divider v-if="includeDivider"
                         class="mb-4"/>

                <!-- Title -->
                <h3 v-html="parsedTitle" class="foxy-footer-title"/>

                <!-- Description -->
                <p v-if="description"
                   v-html="parsedDescription"
                   class="mt-3 mb-2 text-4 foxy-footer-description"
                   :class="descriptionTextClass"/>

                <!-- Button -->
                <Link v-if="buttonLabel && buttonUrl" :url="buttonUrl">
                    <XLButton :label="buttonLabel"
                              :icon="buttonFaIcon"
                              :class="`mt-4`"/>
                </Link>
            </div>
        </div>
    </div>
</template>

<script setup>
import Divider from "/src/vue/components/widgets/Divider.vue"
import {computed} from "vue"
import {useUtils} from "/src/composables/utils.js"
import Link from "/src/vue/components/generic/Link.vue"
import XLButton from "/src/vue/components/widgets/XLButton.vue"

const utils = useUtils()

const props = defineProps({
    title: String,
    description: String,
    includeDivider: Boolean,
    descriptionTextClass: String,
    buttonLabel: String,
    buttonFaIcon: String,
    buttonUrl: String,
})

const parsedTitle = computed(() => {
    return utils.parseCustomText(props.title)
})

const parsedDescription = computed(() => {
    return utils.parseCustomText(props.description)
})
</script>
