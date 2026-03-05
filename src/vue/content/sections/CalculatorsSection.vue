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
