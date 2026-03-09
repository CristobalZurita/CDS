import { computed } from 'vue'

export function useCalculatorsPage() {
  const title = computed(() => 'Calculadoras')
  const subtitle = computed(() => 'Acceso rápido a todas las herramientas')

  const categories = ['Todas', 'Cálculo', 'Identificación', 'Conversión']

  const calculatorItems = computed(() => ([
    {
      label: 'La Máquina del tiempo NE555',
      description: 'Calcula tiempos y configuraciones básicas del 555.',
      path: '/calc/555',
      icon: 'fa-solid fa-stopwatch',
      category: 'Cálculo',
      popular: true,
    },
    {
      label: 'Oscilación CD40106',
      description: 'Frecuencia del Schmitt trigger con R y C.',
      path: '/calc/cd40106',
      icon: 'fa-solid fa-wave-square',
      category: 'Cálculo',
      popular: false,
    },
    {
      label: 'Código de Resistencias',
      description: 'Identifica el valor de resistencias por bandas de color.',
      path: '/calc/resistor-color',
      icon: 'fa-solid fa-palette',
      category: 'Identificación',
      popular: true,
    },
    {
      label: 'Código Capacitores SMD',
      description: 'Convierte códigos SMD a valor de capacitancia.',
      path: '/calc/smd-capacitor',
      icon: 'fa-solid fa-bolt',
      category: 'Identificación',
      popular: true,
    },
    {
      label: 'Ley de Ohm',
      description: 'Calcula voltaje, corriente y resistencia.',
      path: '/calc/ohms-law',
      icon: 'fa-solid fa-plug',
      category: 'Cálculo',
      popular: true,
    },
    {
      label: 'Conversión de Temperatura',
      description: 'Convierte entre Celsius, Fahrenheit y Kelvin.',
      path: '/calc/temperature',
      icon: 'fa-solid fa-temperature-high',
      category: 'Conversión',
      popular: false,
    },
    {
      label: 'Binario, Hex y Decimal',
      description: 'Convierte entre binario, decimal y hexadecimal.',
      path: '/calc/number-system',
      icon: 'fa-solid fa-hashtag',
      category: 'Conversión',
      popular: false,
    },
    {
      label: 'Equivalencia de Longitud',
      description: 'Convierte unidades de medida de longitud.',
      path: '/calc/length',
      icon: 'fa-solid fa-ruler',
      category: 'Conversión',
      popular: false,
    },
    {
      label: 'Grosor de Cable AWG',
      description: 'Calcula conversiones de calibres AWG.',
      path: '/calc/awg',
      icon: 'fa-solid fa-ruler-combined',
      category: 'Identificación',
      popular: false,
    },
  ]))

  const popularItems = computed(() =>
    calculatorItems.value.filter(item => item.popular)
  )

  return {
    title,
    subtitle,
    categories,
    calculatorItems,
    popularItems,
  }
}
