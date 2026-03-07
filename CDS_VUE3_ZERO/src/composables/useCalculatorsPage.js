import { computed } from 'vue'

export function useCalculatorsPage() {
  const title = computed(() => 'Calculadoras')
  const subtitle = computed(() => 'Acceso rápido a todas las herramientas')

  const calculatorItems = computed(() => ([
    {
      label: 'La Máquina del tiempo NE555',
      description: 'Calcula tiempos y configuraciones básicas del 555.',
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
      label: 'Código de Resistencias',
      description: 'Identifica el valor de resistencias por bandas.',
      path: '/calc/resistor-color',
      icon: 'fa-solid fa-palette'
    },
    {
      label: 'Código Capacitores',
      description: 'Convierte códigos SMD a capacitancia.',
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
  ]))

  return {
    title,
    subtitle,
    calculatorItems
  }
}
