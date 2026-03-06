<template>
    <div class="social-links"
         :class="props.class">
        <a v-for="link in parsedLinks"
           class="btn social-link"
           :style="linkStyles"
           :href="link.href"
           target="_blank"
           rel="noopener noreferrer">
            <!-- ToolTip -->
            <div v-if="link.label"
                 class="social-link-tooltip text-1">
                {{link.label}}
            </div>

            <!-- Icon: prefer local svg files, fallback to font-awesome -->
            <div class="social-icon-wrapper">
                <img v-if="link.iconPath" :src="link.iconPath" alt="" class="social-icon-img" />
                <!-- Overlay a font-awesome brand glyph on top of svg square for clearer branding -->
                <i v-if="link.faIcon" :class="link.faIcon + ' social-icon-overlay'"/>
                <i v-else-if="!link.iconPath" :class="link.faIcon"/>
            </div>
        </a>
    </div>
</template>

<script setup>

import { computed } from "vue"
import { useResponsive, COLORS } from "@/composables/useResponsive"
import facebookIcon from "/src/assets/icons/facebook.svg"
import instagramIcon from "/src/assets/icons/instagram.svg"
import twitterIcon from "/src/assets/icons/twitter.svg"
/**
 * @property {Array} items
 * @property {String} size
 * @property {String} variant
 */
const props = defineProps({
    items: Array,
    size: String,
    variant: String,
    class: String
})

const { windowWidth } = useResponsive()

const parsedLinks = computed(() => {
    return (props.items || []).map(item => {
        const href = item.href || "/"
        const label = item.label || ""
        // Prefer local SVGs when available
        let iconPath = null
        const fa = (item.faIcon || '').toLowerCase()
        if (fa.includes('instagram')) iconPath = instagramIcon
        else if (fa.includes('facebook')) iconPath = facebookIcon
        else if (fa.includes('twitter')) iconPath = twitterIcon

        return { href, label, faIcon: item.faIcon || 'fa-solid fa-eye', iconPath }
    })
})

const linkStyles = computed(() => {
    const w = windowWidth.value

    // Default size is 1rem
    let stdFontSize = '1rem'
    let mdDownFontSize = '0.85rem'

    let fontSize = stdFontSize
    let multiplier = 2.4

    if (w <= 1199) {
        fontSize = mdDownFontSize
        multiplier = 2.65
    }

    if (w <= 768) {
        fontSize = mdDownFontSize
        multiplier = 2.4
    }

    return {
        display: 'inline-flex',
        justifyContent: 'center',
        alignItems: 'center',
        marginLeft: '0.25rem',
        marginRight: '0.25rem',
        borderRadius: '100%',
        borderWidth: '2px',
        fontSize,
        width: `calc(${fontSize} * ${multiplier})`,
        height: `calc(${fontSize} * ${multiplier})`,
        color: COLORS.white,
        backgroundColor: '#f07519', // lighten($primary, 10%)
        borderColor: '#faa967' // lighten($primary, 25%)
    }
})
</script>

<style scoped>
.social-link:hover {
    color: #ffffff;
    background-color: #605c56; /* lighten($dark, 15%) */
    border-color: #726d66; /* lighten($dark, 25%) */
}

.social-icon-wrapper {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.social-icon-img {
    width: 1em;
    height: auto;
}
</style>
