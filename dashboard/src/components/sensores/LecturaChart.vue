<template>
  <div class="max-w-full overflow-x-auto custom-scrollbar">
    <div class="-ms-4 min-w-[420px] ps-2">
      <VueApexCharts
        v-if="isMounted"
        type="area"
        :height="altura"
        :options="chartOptions"
        :series="series"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import type { ApexOptions } from 'apexcharts'

const props = withDefaults(
  defineProps<{
    etiquetas: string[]
    datos: number[]
    unidad: string
    min: number
    max: number
    serie?: string
    altura?: number
  }>(),
  {
    serie: 'Lecturas',
    altura: 260,
  },
)

const isMounted = ref(false)

const chartOptions = computed<ApexOptions>(() => {
  const margen = (props.max - props.min) * 0.5 || 1

  return {
    legend: { show: false },
    colors: ['#465FFF'],
    chart: {
      fontFamily: 'Outfit, sans-serif',
      type: 'area',
      toolbar: { show: false },
      zoom: { enabled: false },
    },
    fill: {
      type: 'gradient',
      gradient: { opacityFrom: 0.55, opacityTo: 0 },
    },
    stroke: { curve: 'smooth', width: [2] },
    markers: { size: 0 },
    grid: {
      xaxis: { lines: { show: false } },
      yaxis: { lines: { show: true } },
    },
    dataLabels: { enabled: false },
    annotations: {
      yaxis: [
        {
          y: props.min,
          borderColor: '#12b76a',
          strokeDashArray: 4,
          label: {
            text: `Mín ${props.min}`,
            style: { color: '#fff', background: '#12b76a', fontSize: '11px' },
          },
        },
        {
          y: props.max,
          borderColor: '#12b76a',
          strokeDashArray: 4,
          label: {
            text: `Máx ${props.max}`,
            style: { color: '#fff', background: '#12b76a', fontSize: '11px' },
          },
        },
      ],
    },
    tooltip: {
      y: { formatter: (valor: number) => `${valor} ${props.unidad}` },
    },
    xaxis: {
      type: 'category',
      categories: props.etiquetas,
      axisBorder: { show: false },
      axisTicks: { show: false },
      tooltip: { enabled: false },
    },
    yaxis: {
      min: Math.max(0, props.min - margen),
      max: props.max + margen,
      decimalsInFloat: 1,
    },
  }
})

const series = computed(() => [{ name: props.serie, data: props.datos }])

onMounted(() => {
  isMounted.value = true
})
</script>
