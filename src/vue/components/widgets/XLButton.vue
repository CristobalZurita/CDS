<template>
    <button class="btn btn-primary btn-xl"
                :type="props.type || 'button'"
                :class="[props.class, variant && `btn-${variant}`]"
                @click="props.action ? props.action() : null"
                v-if="props.label || props.action || props.type === 'submit'">
        <i class="me-2" :class="props.icon"/>
        <span v-html="props.label"/>
    </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    class: String,
    label: String,
    type: String,
    icon: String,
    variant: String, // 'orange', 'outline', etc.
    action: Function
})

const variant = computed(() => props.variant)
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";
@import "/src/scss/_variables.scss";

button.btn-xl {
    @include generate-dynamic-styles-with-hash((
        xxxl: (padding: 1.125rem 2.3rem, font-size: 1.125rem),
        xxl:  (padding: 1rem 2rem, font-size: 1rem),
        lg:   (padding: 1rem 1.5rem, font-size: 0.9rem)
    ));

    border-radius: 4rem;
    font-weight: 600;
    font-family: 'Cervo Neue', $headings-font-family;
    text-transform: uppercase;
    transition: all 0.3s ease;
    border: 2px solid transparent;
    letter-spacing: 0.05em;
}

// Variante Orange (Principal CTA)
.btn-orange {
    background-color: $primary !important;
    color: white !important;
    border-color: $primary;

    &:hover {
        background-color: darken($primary, 10%) !important;
        border-color: darken($primary, 10%);
        box-shadow: 0 4px 12px rgba($primary, 0.4);
    }

    &:active {
        background-color: darken($primary, 15%) !important;
    }
}

// Variante Orange Pastel (Principal CTA - Suave)
.btn-orange-pastel {
    background-color: $orange-pastel !important;
    color: white !important;
    border-color: $orange-pastel;

    &:hover {
        background-color: darken($orange-pastel, 10%) !important;
        border-color: darken($orange-pastel, 10%);
        box-shadow: 0 4px 12px rgba($orange-pastel, 0.4);
    }

    &:active {
        background-color: darken($orange-pastel, 15%) !important;
    }
}

// Variante Outline (Secundario)
.btn-outline {
    background-color: transparent !important;
    color: $orange-pastel !important;
    border-color: $orange-pastel;

    &:hover {
        background-color: rgba($orange-pastel, 0.1) !important;
        box-shadow: 0 4px 12px rgba($orange-pastel, 0.2);
    }

    &:active {
        background-color: rgba($orange-pastel, 0.2) !important;
    }
}
</style>