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
      image: '/images/calculadoras/ne555.webp',
      category: 'Cálculo',
      popular: true,
    },
    {
      label: 'Oscilación CD40106',
      description: 'Frecuencia del Schmitt trigger con R y C.',
      path: '/calc/cd40106',
      icon: 'fa-solid fa-wave-square',
      image: '/images/calculadoras/cd40106.webp',
      category: 'Cálculo',
      popular: false,
    },
    {
      label: 'Código de Resistencias',
      description: 'Identifica el valor de resistencias por bandas de color.',
      path: '/calc/resistor-color',
      icon: 'fa-solid fa-palette',
      image: '/images/calculadoras/resistencia.webp',
      category: 'Identificación',
      popular: true,
    },
    {
      label: 'Código Capacitores SMD',
      description: 'Convierte códigos SMD a valor de capacitancia.',
      path: '/calc/smd-capacitor',
      icon: 'fa-solid fa-bolt',
      image: '/images/calculadoras/CAP_SMD_CAL.webp',
      category: 'Identificación',
      popular: false,
    },
    {
      label: 'Ley de Ohm',
      description: 'Calcula voltaje, corriente, resistencia y potencia.',
      path: '/calc/ohms-law',
      icon: 'fa-solid fa-plug',
      image: '/images/calculadoras/leyohm.webp',
      category: 'Cálculo',
      popular: true,
    },
    {
      label: 'Divisor de Voltaje',
      description: 'Calcula Vout, corriente y potencia en el divisor.',
      path: '/calc/voltage-divider',
      icon: 'fa-solid fa-sliders',
      image: '/images/calculadoras/votaje_divider.webp',
      category: 'Cálculo',
      popular: false,
    },
    {
      label: 'Resistores Serie/Paralelo',
      description: 'Resistencia equivalente para redes serie y paralelo.',
      path: '/calc/series-parallel-resistor',
      icon: 'fa-solid fa-diagram-project',
      image: '/images/calculadoras/serie_parallel.webp',
      category: 'Cálculo',
      popular: false,
    },
    {
      label: 'Capacitores Serie/Paralelo',
      description: 'Capacitancia equivalente para redes serie y paralelo.',
      path: '/calc/series-parallel-capacitor',
      icon: 'fa-solid fa-diagram-project',
      image: '/images/calculadoras/cap_serie_parallel.webp',
      category: 'Cálculo',
      popular: false,
    },
    {
      label: 'Constante de Tiempo RC',
      description: 'Calcula tau, corte y carga temporal de circuito RC.',
      path: '/calc/rc-time-constant',
      icon: 'fa-solid fa-clock',
      image: '/images/calculadoras/rc_time.webp',
      category: 'Cálculo',
      popular: false,
    },
    {
      label: 'Filtro Low/High Pass',
      description: 'Calcula frecuencia de corte y ganancia del filtro RC.',
      path: '/calc/low-high-pass-filter',
      icon: 'fa-solid fa-wave-square',
      image: '/images/calculadoras/filters.webp',
      category: 'Cálculo',
      popular: false,
    },
    {
      label: 'Divisor de Corriente',
      description: 'Distribuye corriente en ramas resistivas en paralelo.',
      path: '/calc/current-divider',
      icon: 'fa-solid fa-arrow-down-wide-short',
      image: '/images/calculadoras/corriente_div.webp',
      category: 'Cálculo',
      popular: false,
    },
    {
      label: 'Reactancia',
      description: 'Calcula Xc o Xl según frecuencia y componente.',
      path: '/calc/reactance',
      icon: 'fa-solid fa-signal',
      image: '/images/calculadoras/reacctancia.webp',
      category: 'Cálculo',
      popular: false,
    },
    {
      label: 'Resistor Serie para LED',
      description: 'Calcula resistor y potencia para protección de LEDs.',
      path: '/calc/led-series-resistor',
      icon: 'fa-solid fa-lightbulb',
      image: '/images/calculadoras/led_series_RES.webp',
      category: 'Cálculo',
      popular: true,
    },
    {
      label: 'Conversión de Temperatura',
      description: 'Convierte entre Celsius, Fahrenheit y Kelvin.',
      path: '/calc/temperature',
      icon: 'fa-solid fa-temperature-high',
      image: '/images/calculadoras/temperatura.webp',
      category: 'Conversión',
      popular: false,
    },
    {
      label: 'Binario, Hex y Decimal',
      description: 'Convierte entre binario, decimal y hexadecimal.',
      path: '/calc/number-system',
      icon: 'fa-solid fa-hashtag',
      image: '/images/calculadoras/HEX.webp',
      category: 'Conversión',
      popular: false,
    },
    {
      label: 'Equivalencia de Longitud',
      description: 'Convierte unidades de medida de longitud.',
      path: '/calc/length',
      icon: 'fa-solid fa-ruler',
      image: '/images/calculadoras/longitud.webp',
      category: 'Conversión',
      popular: false,
    },
    {
      label: 'Grosor de Cable AWG',
      description: 'Calcula conversiones de calibres AWG.',
      path: '/calc/awg',
      icon: 'fa-solid fa-ruler-combined',
      image: '/images/calculadoras/awg.webp',
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
