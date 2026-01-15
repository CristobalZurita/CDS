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

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

@mixin create-btn-social-size($std-font-size, $md-down-font-size) {
    $font-size: $std-font-size;

    font-size: $font-size;
    width: calc($font-size * 2.4);
    height: calc($font-size * 2.4);

    @include media-breakpoint-down(xl) {
        font-size: $md-down-font-size;
        width: calc($md-down-font-size * 2.65);
        height: calc($md-down-font-size * 2.65);
    }

    @include media-breakpoint-down(md) {
        font-size: $md-down-font-size;
        width: calc($md-down-font-size * 2.4);
        height: calc($md-down-font-size * 2.4);
    }
}

@mixin create-btn-social-color($color, $bg-color, $border-color, $hover-color, $hover-bg-color, $hover-border-color) {
    color: $color;
    background-color: $bg-color;
    border-color: $border-color;

    &:hover {
        color: $hover-color;
        background-color: $hover-bg-color;
        border-color: $hover-border-color;
    }
}

a.social-link {
    display: inline-flex;
    justify-content: center;
    align-items: center;

    margin-left: 0.25rem;
    margin-right: 0.25rem;

    border-radius: 100%;
    border-width: 2px;
    color: $white;

    @include create-btn-social-size(1rem, 0.85rem);
    @include create-btn-social-color(
        $white, lighten($primary, 10%), lighten($primary, 25%),
        $white, lighten($dark, 15%), lighten($dark, 25%),
    )
}

.social-icon-wrapper {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.social-icon-img {
    width: 1em;
    height: 1em;
    display: block;
}

.social-icon-overlay {
    position: absolute;
    color: $white;
    font-size: 0.9em;
    pointer-events: none;
}

a.social-link-size-2 {
    @include create-btn-social-size(1.2rem, 1rem);
    .social-link-tooltip {
        margin-top: -5rem;
    }
}

a.social-link-size-3 {
    @include create-btn-social-size(1.4rem, 1.2rem);
    .social-link-tooltip {
        margin-top: -6rem;
    }
}

a.social-link-size-4 {
    @include create-btn-social-size(1.8rem, 1.6rem);
    .social-link-tooltip {
        margin-top: -7.5rem;
    }
}

a.social-link-color-dark {
    @include create-btn-social-color(
        $white, $dark, $white,
        $primary, $white, $white
    )
}

a.social-link-color-secondary {
    @include create-btn-social-color(
        $white, $dark, lighten($dark, 10%),
        $white, $primary, darken($primary, 5%)
    )
}

a.social-link-color-black {
    @include create-btn-social-color(
        $white, lighten($black, 7%), lighten($black, 13%),
        $white, $primary, darken($primary, 5%)
    )
}

a.social-link-color-light {
    @include create-btn-social-color(
        $white, lighten($dark, 5%), lighten($dark, 20%),
        $white, lighten($primary, 5%), lighten($primary, 20%),
    )
}

div.social-link-tooltip {
    position: absolute;
    text-transform: capitalize;
    background-color: darken($primary, 10%);
    color:$text-normal-contrast;
    padding: 0.2rem 0.6rem;
    border-radius: 10px;
    display: none;

    &::before {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: darken($primary, 10%) transparent transparent transparent;
    }
}

a.social-link:hover {
    .social-link-tooltip {
        @include media-breakpoint-up(md) {
            display: block!important;
        }
    }
}
</style>