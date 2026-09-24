<template>
  <AdminLayout>
    <h1 class="font-medium text-4xl pb-5">¡Bienvenido!</h1>
    <h2 class="font-medium text-2xl pb-5">Resumen de lecturas recientes del Invernadero 2.</h2>

    <div class="space-y-5 pb-6 sm:space-y-6">
      <div class="flex flex-wrap items-center gap-x-3 gap-y-2">
        <span
          class="inline-flex items-center rounded-full bg-brand-50 px-2.5 py-1 text-theme-xs font-medium text-brand-500 dark:bg-brand-500/15 dark:text-brand-400"
        >
          {{ tanquesVista.length }} tanques en {{ camas.size }} camas de cultivo
        </span>
        <span
          v-for="info in contexto"
          :key="info"
          class="text-theme-sm text-gray-500 dark:text-gray-400"
        >
          {{ info }}
        </span>
      </div>

      <section>
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
              Ambiente del invernadero
            </h3>
            <p class="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">
              Temperatura y humedad · {{ textoRango }} · línea verde = rango normal
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

        <div class="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2 md:gap-6">
          <article
            v-for="lectura in ambiente"
            :key="lectura.sensor.id"
            class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6"
          >
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h4 class="text-base font-semibold text-gray-800 dark:text-white/90">
                  {{ lectura.titulo }}
                </h4>
                <p class="mt-0.5 text-theme-xs text-gray-500 dark:text-gray-400">
                  {{ lectura.sensor.codigo }} · {{ lectura.sensor.nombre }}
                </p>
              </div>

              <EstadoSensor :estado="lectura.sensor.estado" :alerta="enAlerta(lectura.sensor)" />
            </div>

            <div class="mt-3 flex flex-wrap items-baseline justify-between gap-2">
              <p class="flex items-baseline gap-1.5">
                <span class="text-title-md font-bold text-gray-800 dark:text-white/90">
                  {{ lectura.sensor.ultimaLectura.valor }}
                </span>
                <span class="text-theme-sm text-gray-500 dark:text-gray-400">
                  {{ tipoSensor[lectura.sensor.tipo].unidad }}
                </span>
              </p>
              <p class="text-theme-xs text-gray-500 dark:text-gray-400">
                Rango {{ lectura.sensor.rangoNormal.min }} – {{ lectura.sensor.rangoNormal.max }} ·
                lectura {{ formatoHora(lectura.sensor.ultimaLectura.fecha) }}
              </p>
            </div>

            <div class="mt-4">
              <LecturaChart
                :etiquetas="etiquetas"
                :datos="datosDe(lectura.sensor)"
                :unidad="tipoSensor[lectura.sensor.tipo].unidad"
                :min="lectura.sensor.rangoNormal.min"
                :max="lectura.sensor.rangoNormal.max"
                :serie="lectura.titulo"
                :altura="240"
              />
            </div>

            <div class="mt-3 flex justify-end border-t border-gray-100 pt-3 dark:border-gray-800">
              <router-link
                :to="{ name: 'SensorDetalle', params: { id: lectura.sensor.id } }"
                class="text-theme-xs font-medium text-brand-500 hover:text-brand-600 dark:text-brand-400"
              >
                Ver detalle
              </router-link>
            </div>
          </article>
        </div>
      </section>

      <section>
        <div>
          <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
            Tanques del invernadero
          </h3>
          <p class="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">
            {{ tanquesVista.length }} tanques en {{ camas.size }} camas · clic en un sensor para ver
            su desglose con históricos
          </p>
        </div>

        <div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3 md:gap-6">
          <article
            v-for="fila in tanquesVista"
            :key="fila.tanque.id"
            class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6"
          >
            <header class="flex flex-wrap items-start justify-between gap-2">
              <div>
                <h4 class="text-base font-semibold text-gray-800 dark:text-white/90">
                  {{ fila.tanque.nombre }}
                </h4>
                <p class="mt-0.5 text-theme-xs text-gray-500 dark:text-gray-400">
                  Capacidad {{ fila.tanque.capacidadLitros.toLocaleString('es-AR') }} L
                </p>
              </div>
              <span
                class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-theme-xs font-medium text-gray-700 dark:bg-white/5 dark:text-white/80"
              >
                {{ fila.tanque.cama }}
              </span>
            </header>

            <div class="mt-4 rounded-xl bg-gray-50 p-3 dark:bg-white/[0.03]">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span class="text-theme-xs font-medium text-gray-500 dark:text-gray-400">
                  Nivel de agua
                </span>
                <EstadoSensor :estado="fila.nivel.estado" :alerta="enAlerta(fila.nivel)" />
              </div>

              <div class="mt-2 flex flex-wrap items-baseline gap-1.5">
                <span
                  class="text-title-sm font-bold"
                  :class="claseNivel(fila.nivel.ultimaLectura.valor)"
                >
                  {{ fila.nivel.ultimaLectura.valor }}%
                </span>
                <span class="text-theme-xs text-gray-500 dark:text-gray-400">
                  {{ litrosDe(fila) }} L disponibles
                </span>
              </div>

              <div
                class="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800"
              >
                <span
                  class="block h-full rounded-full"
                  :class="barraNivel(fila.nivel.ultimaLectura.valor)"
                  :style="{ width: fila.nivel.ultimaLectura.valor + '%' }"
                ></span>
              </div>

              <p
                class="mt-2 text-theme-xs font-medium"
                :class="
                  estadoBombeo(fila).alerta
                    ? 'text-error-600 dark:text-error-500'
                    : 'text-success-600 dark:text-success-500'
                "
              >
                {{ estadoBombeo(fila).texto }}
              </p>

              <p class="mt-1.5 text-theme-xs text-gray-500 dark:text-gray-400">
                {{ fila.nivel.codigo }} · lectura {{ formatoHora(fila.nivel.ultimaLectura.fecha) }}
              </p>
            </div>

            <div class="mt-3 space-y-3">
              <router-link
                v-for="medicion in medicionesDe(fila)"
                :key="medicion.sensor.id"
                :to="{ name: 'SensorDetalle', params: { id: medicion.sensor.id } }"
                class="block rounded-xl border border-gray-100 p-3 transition hover:border-brand-300 hover:bg-gray-50 dark:border-gray-800 dark:hover:border-brand-500/40 dark:hover:bg-white/[0.03]"
              >
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <span class="text-theme-sm font-medium text-gray-800 dark:text-white/90">
                    {{ medicion.etiqueta }}
                  </span>
                  <EstadoSensor
                    :estado="medicion.sensor.estado"
                    :alerta="enAlerta(medicion.sensor)"
                  />
                </div>

                <div class="mt-1.5 flex items-baseline gap-1.5">
                  <span class="text-title-sm font-bold text-gray-800 dark:text-white/90">
                    {{ medicion.sensor.ultimaLectura.valor }}
                  </span>
                  <span class="text-theme-xs text-gray-500 dark:text-gray-400">
                    {{ tipoSensor[medicion.sensor.tipo].unidad }}
                  </span>
                </div>

                <p class="mt-1 text-theme-xs text-gray-500 dark:text-gray-400">
                  Rango {{ medicion.sensor.rangoNormal.min }} –
                  {{ medicion.sensor.rangoNormal.max }} · lectura
                  {{ formatoHora(medicion.sensor.ultimaLectura.fecha) }}
                </p>

                <div class="mt-2 flex items-center justify-between">
                  <span class="text-theme-xs text-gray-500 dark:text-gray-400">
                    {{ medicion.sensor.codigo }}
                  </span>
                  <span class="text-theme-xs font-medium text-brand-500 dark:text-brand-400">
                    Ver desglose
                    <span class="inline-block rtl:rotate-180">→</span>
                  </span>
                </div>
              </router-link>
            </div>
          </article>
        </div>
      </section>
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
  sensoresDelTanque,
  tanquesDeInvernadero,
  tipoSensor,
  type Sensor,
  type Tanque,
} from '@/data/mockSensores'

const nombreInvernadero = 'Invernadero 2'

interface LecturaAmbiente {
  titulo: string
  sensor: Sensor
}

const metricasAmbiente = [
  { tipo: 'temperatura', titulo: 'Temperatura' },
  { tipo: 'humedad_aire', titulo: 'Humedad' },
] as const

const ambiente = computed<LecturaAmbiente[]>(() => {
  const items: LecturaAmbiente[] = []
  for (const metrica of metricasAmbiente) {
    const sensor = sensores.find(
      (item) =>
        item.tipo === metrica.tipo && sectorPorId(item.sectorId)?.invernadero === nombreInvernadero,
    )
    if (sensor) items.push({ titulo: metrica.titulo, sensor })
  }
  return items
})

interface FilaTanque {
  tanque: Tanque
  nivel: Sensor
  ph: Sensor
  ec: Sensor
}

const tanquesVista = computed<FilaTanque[]>(() => {
  const items: FilaTanque[] = []
  for (const tanque of tanquesDeInvernadero(nombreInvernadero)) {
    const delTanque = sensoresDelTanque(tanque)
    if (delTanque) items.push({ tanque, ...delTanque })
  }
  return items
})

const camas = computed(() => new Set(tanquesVista.value.map((fila) => fila.tanque.cama)))

function medicionesDe(fila: FilaTanque) {
  return [
    { etiqueta: 'pH', sensor: fila.ph },
    { etiqueta: 'Conductividad', sensor: fila.ec },
  ]
}

function claseNivel(valor: number) {
  if (valor <= 20) return 'text-error-600 dark:text-error-500'
  if (valor <= 50) return 'text-warning-600 dark:text-orange-400'
  return 'text-gray-800 dark:text-white/90'
}

function barraNivel(valor: number) {
  if (valor <= 20) return 'bg-error-500'
  if (valor <= 50) return 'bg-warning-500'
  return 'bg-success-500'
}

function litrosDe(fila: FilaTanque) {
  const litros = Math.round((fila.tanque.capacidadLitros * fila.nivel.ultimaLectura.valor) / 100)
  return litros.toLocaleString('es-AR')
}

function estadoBombeo(fila: FilaTanque) {
  const valor = fila.nivel.ultimaLectura.valor
  if (valor < fila.nivel.rangoNormal.min) {
    return { texto: 'Nivel de agua bajo — posible problema de bombeo', alerta: true }
  }
  if (valor > fila.nivel.rangoNormal.max) {
    return { texto: 'Nivel de agua fuera de rango — revisar bombeo', alerta: true }
  }
  return { texto: 'Bombeo sin novedades', alerta: false }
}

const contexto = computed(() => {
  const lineas: string[] = []
  for (const sector of sectores.filter((item) => item.invernadero === nombreInvernadero)) {
    const datosSector = [sector.nombre, sector.invernadero, sector.superficie].filter(Boolean)
    lineas.push(datosSector.join(' · '))
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
