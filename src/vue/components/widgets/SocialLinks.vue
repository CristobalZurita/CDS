<template>
    <div class="social-links"
         :class="props.class">
        <a v-for="link in parsedLinks"
           class="btn social-link"
           :class="classList"
           :href="link.href"
           target="_blank">
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

import {computed} from "vue"
import facebookIcon from "/src/assets/icons/facebook.svg"
import instagramIcon from "/src/assets/icons/instagram.svg"
import twitterIcon from "/src/assets/icons/twitter.svg"
/**
 * @property {Array} items
 * @property {String} size
 * @property {String} color
 */
const props = defineProps({
    items: Array,
    size: String,
    variant: String,
    class: String
})

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

const classList = computed(() => {
    const sizeClass = "social-link-size-" + props.size
    const colorClass = "social-link-color-" + props.variant
    return sizeClass + " " + colorClass
})
</script>
