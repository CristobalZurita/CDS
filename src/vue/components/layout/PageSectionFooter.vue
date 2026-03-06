<template>
    <div :style="footerStyles">
        <div class="row">
            <div :style="footerContentStyles" class="col-12 col-lg-8">
                <Divider v-if="includeDivider" :style="{ marginBottom: '1.5rem' }"/>

                <h3 :style="titleStyles" v-html="parsedTitle"/>

                <p v-if="description"
                   v-html="parsedDescription"
                   :style="descriptionStyles"
                   :class="descriptionTextClass"/>

                <Link v-if="buttonLabel && buttonUrl" :url="buttonUrl">
                    <XLButton :label="buttonLabel"
                              :icon="buttonFaIcon"
                              :style="{ marginTop: '1.5rem' }"/>
                </Link>
            </div>
        </div>
    </div>
</template>

<script setup>
import Divider from "@/vue/components/widgets/Divider.vue"
import { computed } from "vue"
import { useUtils } from "@/composables/utils.js"
import Link from "@/vue/components/generic/Link.vue"
import XLButton from "@/vue/components/widgets/XLButton.vue"
import { useResponsive, COLORS, getResponsiveValue } from "@/composables/useResponsive"

const utils = useUtils()
const { windowWidth } = useResponsive()

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

// Margin-top responsive
const footerMarginTop = computed(() => {
    return getResponsiveValue({
        xxxl: '2rem',
        xxl: '1.5rem',
        lg: '1.1rem',
        md: '1.05rem',
        sm: '0.75rem'
    }, windowWidth.value)
})

const footerStyles = computed(() => ({
    marginTop: footerMarginTop.value,
    textAlign: 'center'
}))

const footerContentStyles = computed(() => ({
    textAlign: 'center',
    margin: '0 auto'
}))

const titleStyles = computed(() => ({
    fontFamily: "'Cervo Neue', 'Steelfish', serif",
    fontWeight: '800',
    letterSpacing: '0.03em',
    color: COLORS.dark,
    textTransform: 'uppercase'
}))

const descriptionStyles = computed(() => ({
    fontFamily: "'Cervo Neue', system-ui, sans-serif",
    fontWeight: '400',
    lineHeight: '1.6',
    marginTop: '1rem',
    marginBottom: '0.5rem'
}))
</script>
