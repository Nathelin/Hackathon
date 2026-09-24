<template>
  <AdminLayout>
    <h1 class="font-medium text-4xl pb-5">¡Bienvenido!</h1>
    <h2 class="font-medium text-2xl pb-5">Resumen de lecturas recientes del Invernadero 2.</h2>

    <div class="space-y-5 pb-6 sm:space-y-6">
      <div class="flex flex-wrap items-center gap-x-3 gap-y-2">
        <span
          class="inline-flex items-center rounded-full bg-brand-50 px-2.5 py-1 text-theme-xs font-medium text-brand-500 dark:bg-brand-500/15 dark:text-brand-400"
        >
          Tanque único de nutrientes
        </span>
        <span
          v-for="info in contexto"
          :key="info"
          class="text-theme-sm text-gray-500 dark:text-gray-400"
        >
          {{ info }}
        </span>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4 md:gap-6">
        <router-link
          v-for="lectura in lecturas"
          :key="lectura.sensor.id"
          :to="{ name: 'SensorDetalle', params: { id: lectura.sensor.id } }"
          class="block rounded-2xl border border-gray-200 bg-white p-5 transition hover:border-brand-300 hover:shadow-theme-sm dark:border-gray-800 dark:bg-white/[0.03] dark:hover:border-brand-500/40 md:p-6"
        >
          <div class="flex flex-wrap items-start justify-between gap-2">
            <p class="text-theme-sm text-gray-500 dark:text-gray-400">
              {{ lectura.metrica.titulo }}
            </p>
            <EstadoSensor :estado="lectura.sensor.estado" :alerta="enAlerta(lectura.sensor)" />
          </div>

          <div class="mt-3 flex items-baseline gap-1.5">
            <span class="text-title-md font-bold text-gray-800 dark:text-white/90">
              {{ lectura.sensor.ultimaLectura.valor }}
            </span>
            <span class="text-theme-sm text-gray-500 dark:text-gray-400">
              {{ tipoSensor[lectura.sensor.tipo].unidad }}
            </span>
          </div>

          <p class="mt-2 text-theme-xs text-gray-500 dark:text-gray-400">
            Rango {{ lectura.sensor.rangoNormal.min }} – {{ lectura.sensor.rangoNormal.max }} ·
            lectura
            {{ formatoHora(lectura.sensor.ultimaLectura.fecha) }}
          </p>
        </router-link>
      </div>

      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
            Histórico de lecturas
          </h3>
          <p class="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">
            {{ textoRango }} · línea verde = rango normal de la métrica
          </p>
        </div>

        <div
          class="flex max-h-10 items-center gap-0.5 self-start rounded-lg bg-gray-100 p-0.5 dark:bg-gray-900"
        >
          <button
            v-for="opcion in rangosGrafico"
            :key="opcion.valor"
            type="button"
            :class="[
              rangoGrafico === opcion.valor
                ? 'shadow-theme-xs bg-white text-gray-900 dark:bg-gray-800 dark:text-white'
                : 'text-gray-500 dark:text-gray-400',
              'rounded-md px-3 py-2 text-theme-sm font-medium whitespace-nowrap hover:text-gray-900 dark:hover:text-white',
            ]"
            @click="rangoGrafico = opcion.valor"
          >
            {{ opcion.etiqueta }}
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 xl:grid-cols-2 md:gap-6">
        <section
          v-for="lectura in lecturas"
          :key="lectura.sensor.id"
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6"
        >
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h4 class="text-base font-semibold text-gray-800 dark:text-white/90">
                {{ lectura.metrica.titulo }}
              </h4>
              <p class="mt-0.5 text-theme-xs text-gray-500 dark:text-gray-400">
                {{ lectura.metrica.fuente }}
              </p>
            </div>

            <p class="text-end text-theme-xs text-gray-500 dark:text-gray-400">
              Rango {{ lectura.sensor.rangoNormal.min }} –
              {{ lectura.sensor.rangoNormal.max }}
              {{ tipoSensor[lectura.sensor.tipo].unidad }}
            </p>
          </div>

          <div class="mt-4">
            <LecturaChart
              :etiquetas="etiquetas"
              :datos="datosDe(lectura.sensor)"
              :unidad="tipoSensor[lectura.sensor.tipo].unidad"
              :min="lectura.sensor.rangoNormal.min"
              :max="lectura.sensor.rangoNormal.max"
              :serie="lectura.metrica.titulo"
              :altura="240"
            />
          </div>

          <div
            class="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-gray-100 pt-3 dark:border-gray-800"
          >
            <p class="text-theme-xs text-gray-500 dark:text-gray-400">
              {{ lectura.sensor.codigo }} · {{ lectura.sensor.nombre }}
            </p>
            <router-link
              :to="{ name: 'SensorDetalle', params: { id: lectura.sensor.id } }"
              class="text-theme-xs font-medium text-brand-500 hover:text-brand-600 dark:text-brand-400"
            >
              Ver detalle
            </router-link>
          </div>
        </section>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import EstadoSensor from '@/components/sensores/EstadoSensor.vue'
import LecturaChart from '@/components/sensores/LecturaChart.vue'
import {
  diasDesde,
  enAlerta,
  etiquetas24h,
  etiquetas7d,
  formatoFecha,
  formatoHora,
  plantaciones,
  sectorPorId,
  sectores,
  sensores,
  tipoSensor,
  type Sensor,
} from '@/data/mockSensores'

const nombreInvernadero = 'Invernadero 2'

const metricas = [
  { tipo: 'ph', titulo: 'pH', fuente: 'Tanque único de nutrientes' },
  { tipo: 'ec', titulo: 'Conductividad eléctrica', fuente: 'Tanque único de nutrientes' },
  { tipo: 'humedad_aire', titulo: 'Humedad', fuente: 'Ambiente del invernadero' },
  { tipo: 'temperatura', titulo: 'Temperatura', fuente: 'Ambiente del invernadero' },
] as const

interface LecturaMetrica {
  metrica: (typeof metricas)[number]
  sensor: Sensor
}

const lecturas = computed<LecturaMetrica[]>(() => {
  const items: LecturaMetrica[] = []
  for (const metrica of metricas) {
    const sensor = sensores.find(
      (item) =>
        item.tipo === metrica.tipo && sectorPorId(item.sectorId)?.invernadero === nombreInvernadero,
    )
    if (sensor) items.push({ metrica, sensor })
  }
  return items
})

const contexto = computed(() => {
  const lineas: string[] = []
  for (const sector of sectores.filter((item) => item.invernadero === nombreInvernadero)) {
    lineas.push(`${sector.nombre} · ${sector.invernadero} · ${sector.superficie}`)
    for (const plantacion of plantaciones.filter((item) => item.sectorId === sector.id)) {
      lineas.push(
        `${plantacion.cultivo} · var. ${plantacion.variedad} · siembra ${formatoFecha(
          plantacion.fechaSiembra,
        )} (${diasDesde(plantacion.fechaSiembra)} días de ciclo)`,
      )
    }
  }
  return lineas
})

const rangoGrafico = ref<'24h' | 'd7'>('24h')

const rangosGrafico = [
  { valor: '24h' as const, etiqueta: 'Últimas 24 h' },
  { valor: 'd7' as const, etiqueta: 'Últimos 7 días' },
]

const etiquetas = computed(() => (rangoGrafico.value === '24h' ? etiquetas24h : etiquetas7d))

const textoRango = computed(() =>
  rangoGrafico.value === '24h' ? 'Últimas 24 horas' : 'Últimos 7 días',
)

function datosDe(sensor: Sensor) {
  return rangoGrafico.value === '24h' ? sensor.serie24h : sensor.serie7d
}
</script>
