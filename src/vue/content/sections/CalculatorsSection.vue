<template>
    <PageSection variant="default"
                 :id="props.id">
        <PageSectionHeader title="*Calculadoras*"
                           subtitle="Acceso rapido a todas las herramientas"/>

        <PageSectionContent>
            <div class="calculators-grid">
                <Link v-for="item in calculatorItems"
                      :key="item.path"
                      :url="item.path">
                    <div class="calculator-card">
                        <div class="calculator-card-icon">
                            <i :class="item.icon"/>
                        </div>
                        <div class="calculator-card-content">
                            <h3>{{ item.label }}</h3>
                            <p>{{ item.description }}</p>
                        </div>
                    </div>
                </Link>
            </div>

            <div class="calculators-actions">
                <Link url="/">
                    <XLButton label="VOLVER AL INICIO"
                              icon="fa-solid fa-arrow-left"
                              variant="outline"/>
                </Link>
            </div>
        </PageSectionContent>
    </PageSection>
</template>

<script setup>
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionHeader from "/src/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"
import Link from "/src/vue/components/generic/Link.vue"
import XLButton from "/src/vue/components/widgets/XLButton.vue"

const props = defineProps({
    id: String
})

const calculatorItems = [
    {
        label: 'La Máquina del tiempo NE555',
        description: 'Calcula tiempos y configuraciones basicas del 555.',
        path: '/calc/555',
        icon: 'fa-solid fa-stopwatch'
    },
    {
        label: 'Calcula oscilación CD40106',
        description: 'Frecuencia del Schmitt trigger con R y C.',
        path: '/calc/smd-resistor',
        icon: 'fa-solid fa-wave-square'
    },
    {
        label: 'Codigo de Resistencias',
        description: 'Identifica el valor de resistencias por bandas.',
        path: '/calc/resistor-color',
        icon: 'fa-solid fa-palette'
    },
 
    {
        label: 'Código Capacitores ',
        description: 'Convierte codigos SMD a capacitancia.',
        path: '/calc/smd-capacitor',
        icon: 'fa-solid fa-bolt'
    },
    {
        label: 'Calcula la Ley de Ohm',
        description: 'Calcula voltaje, corriente y resistencia.',
        path: '/calc/ohms-law',
        icon: 'fa-solid fa-plug'
    },
    {
        label: 'Convierte Temperatura',
        description: 'Convierte Celsius, Fahrenheit y Kelvin.',
        path: '/calc/temperature',
        icon: 'fa-solid fa-temperature-high'
    },
    {
        label: 'Binario, Hexadecimal y Decimal',
        description: 'Convierte entre binario, decimal y hex.',
        path: '/calc/number-system',
        icon: 'fa-solid fa-hashtag'
    },
    {
        label: 'Equivalencia de Longitud',
        description: 'Convierte unidades de medida.',
        path: '/calc/length',
        icon: 'fa-solid fa-ruler'
    },
    {
        label: 'Calcular Grosor Cable AWG',
        description: 'Calcula conversiones de calibres AWG.',
        path: '/calc/awg',
        icon: 'fa-solid fa-ruler-combined'
    }
]
</script>

<style lang="scss" scoped>
@use "@/scss/_theming.scss" as *;

.calculators-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.25rem;

    @include media-breakpoint-down(lg) {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    @include media-breakpoint-down(sm) {
        grid-template-columns: 1fr;
    }
}

.calculators-grid :deep(a) {
    text-decoration: none;
}

.calculator-card {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    padding: 1.25rem 1.35rem;
    border: 1px solid rgba($dark, 0.12);
    border-radius: 18px;
    background: linear-gradient(135deg, rgba($light-1, 0.7), rgba($light-2, 0.25));
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.calculator-card:hover {
    transform: translateY(-4px);
    border-color: rgba($primary, 0.35);
    box-shadow: 0 16px 28px rgba($dark, 0.12);
}

.calculator-card-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: rgba($primary, 0.12);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: $primary;
    font-size: 1.1rem;
}

.calculator-card-content h3 {
    font-family: 'Cervo Neue', $headings-font-family;
    font-weight: 700;
    font-size: 1rem;
    margin: 0 0 0.35rem;
    color: $dark;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.calculator-card-content p {
    margin: 0;
    color: $text-muted;
    font-family: 'Cervo Neue', $font-family-base;
    font-size: 0.9rem;
    line-height: 1.45;
}

.calculators-actions {
    margin-top: 2.5rem;
    display: flex;
    justify-content: center;
}
</style>
