<template>
    <button class="btn btn-primary xl-button"
                :type="props.type || 'button'"
                :class="[props.class, variant && `btn-${variant}`]"
                :style="buttonStyles"
                @click="props.action ? props.action() : null"
                v-if="props.label || props.action || props.type === 'submit'">
        <i class="me-2" :class="props.icon"/>
        <span v-html="props.label"/>
    </button>
</template>

<script setup>
import { computed } from 'vue'
import { useResponsive, getResponsiveValue } from "@/composables/useResponsive"

const props = defineProps({
    class: String,
    label: String,
    type: String,
    icon: String,
    variant: String, // 'orange', 'orange-pastel', 'outline'
    action: Function
})

const { windowWidth } = useResponsive()
const variant = computed(() => props.variant)

const buttonStyles = computed(() => {
    const padding = getResponsiveValue({
        xxxl: '1.125rem 2.3rem',
        xxl: '1rem 2rem',
        lg: '1rem 1.5rem',
        md: '1rem 1.5rem',
        sm: '1rem 1.5rem'
    }, windowWidth.value)

    const fontSize = getResponsiveValue({
        xxxl: '1.125rem',
        xxl: '1rem',
        lg: '0.9rem',
        md: '0.9rem',
        sm: '0.9rem'
    }, windowWidth.value)

    return {
        padding,
        fontSize,
        borderRadius: '4rem',
        fontWeight: '600',
        fontFamily: "'Cervo Neue', 'Steelfish', serif",
        textTransform: 'uppercase',
        transition: 'all 0.3s ease',
        border: '2px solid transparent',
        letterSpacing: '0.05em'
    }
})
</script>

<style scoped>
/* Variante Orange (Principal CTA) */
.xl-button.btn-orange {
    background-color: #ec6b00 !important;
    color: #ffffff !important;
    border-color: #ec6b00;
}

.xl-button.btn-orange:hover {
    background-color: #c95800 !important;
    border-color: #c95800;
    box-shadow: 0 4px 12px rgba(236, 107, 0, 0.4);
}

.xl-button.btn-orange:active {
    background-color: #b34f00 !important;
}

/* Variante Orange Pastel (Principal CTA - Suave) */
.xl-button.btn-orange-pastel {
    background-color: #e8935a !important;
    color: #ffffff !important;
    border-color: #e8935a;
}

.xl-button.btn-orange-pastel:hover {
    background-color: #d4732e !important;
    border-color: #d4732e;
    box-shadow: 0 4px 12px rgba(232, 147, 90, 0.4);
}

.xl-button.btn-orange-pastel:active {
    background-color: #c2651a !important;
}

/* Variante Outline (Secundario) */
.xl-button.btn-outline {
    background-color: transparent !important;
    color: #e8935a !important;
    border-color: #e8935a;
}

.xl-button.btn-outline:hover {
    background-color: rgba(232, 147, 90, 0.1) !important;
    box-shadow: 0 4px 12px rgba(232, 147, 90, 0.2);
}

.xl-button.btn-outline:active {
    background-color: rgba(232, 147, 90, 0.2) !important;
}
</style>
