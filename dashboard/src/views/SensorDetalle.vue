<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="Detalle del dispositivo" />

    <div v-if="dispositivo" class="space-y-5 sm:space-y-6">
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6"
      >
        <router-link
          to="/sensores"
          class="inline-flex items-center gap-1.5 text-theme-sm text-gray-500 transition hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <ChevronRightIcon class="h-4 w-4 rotate-180 rtl:rotate-0" />
          Volver al listado
        </router-link>

        <div class="mt-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="text-title-xl font-semibold text-gray-800 dark:text-white/90">
                {{ dispositivo.codigo }}
              </h2>
              <EstadoSensor :estado="dispositivo.estado" :alerta="enAlerta(dispositivo)" />
            </div>
            <p class="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">
              {{ dispositivo.nombre }} · {{ etiquetasMediciones }}
            </p>
          </div>

          <p class="text-theme-sm text-gray-500 dark:text-gray-400">
            Última lectura: {{ formatoFechaHora(fechaUltimaLectura(dispositivo)) }}
          </p>
        </div>
      </div>

      <!--div class="grid grid-cols-1 gap-4 sm:grid-cols-3 md:gap-6">
        <div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6"
        >
          <p class="text-theme-sm text-gray-500 dark:text-gray-400">Mediciones</p>
          <div class="mt-2 flex items-baseline gap-1.5">
            <h4 class="text-title-lg font-bold text-gray-800 dark:text-white/90">
              {{ dispositivo.mediciones.length }}
            </h4>
            <span class="text-theme-sm text-gray-500 dark:text-gray-400">
              {{ dispositivo.mediciones.length === 1 ? 'sensor' : 'sensores' }}
            </span>
          </div>
          <p class="mt-1 text-theme-xs text-gray-500 dark:text-gray-400">
            {{ etiquetasMediciones }}
          </p>
        </div>

        <!--div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6"
        >
          <p class="text-theme-sm text-gray-500 dark:text-gray-400">Batería</p>
          <div class="mt-2 flex items-baseline gap-1.5">
            <h4 :class="['text-title-lg font-bold', claseBateria(dispositivo.bateria)]">
              {{ dispositivo.bateria }}%
            </h4>
          </div>
          <div class="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
            <div
              :class="['h-full rounded-full', claseBarra(dispositivo.bateria)]"
              :style="{ width: dispositivo.bateria + '%' }"
            ></div>
          </div>
        </div>

        <div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6"
        >
          <p class="text-theme-sm text-gray-500 dark:text-gray-400">Señal</p>
          <div class="mt-2 flex items-baseline gap-1.5">
            <h4 class="text-title-lg font-bold text-gray-800 dark:text-white/90">
              {{ dispositivo.senal }}%
            </h4>
          </div>
          <p class="mt-1 text-theme-xs text-gray-500 dark:text-gray-400">
            {{ dispositivo.senal === 0 ? 'Sin enlace con el gateway' : 'Conectado por LoRaWAN' }}
          </p>
        </div>
      </div-->

      <div class="grid grid-cols-12 gap-4 md:gap-6">
        <div class="col-span-12 xl:col-span-8">
          <div
            class="rounded-2xl border border-gray-200 bg-white px-5 pb-5 pt-5 dark:border-gray-800 dark:bg-white/[0.03] sm:px-6 sm:pt-6"
          >
            <div class="flex flex-col gap-4 mb-6 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
                  Qué está leyendo el dispositivo
                </h3>
                <p class="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">
                  {{ etiquetasMediciones }} en {{ ubicacionDispositivo }}
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

            <div class="space-y-6">
              <section
                v-for="(medicion, index) in dispositivo.mediciones"
                :key="medicion.tipo"
                :class="[index > 0 ? 'border-t border-gray-100 pt-6 dark:border-gray-800' : '']"
              >
                <div class="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h4 class="text-base font-semibold text-gray-800 dark:text-white/90">
                      {{ tipoSensor[medicion.tipo].label }}
                    </h4>
                    <p class="mt-0.5 text-theme-xs text-gray-500 dark:text-gray-400">
                      Rango {{ medicion.rangoNormal.min }} – {{ medicion.rangoNormal.max }}
                      {{ tipoSensor[medicion.tipo].unidad }} · lectura
                      {{ formatoHora(medicion.ultimaLectura.fecha) }}
                    </p>
                  </div>

                  <div class="flex items-baseline gap-1.5">
                    <span class="text-title-md font-bold text-gray-800 dark:text-white/90">
                      {{ medicion.ultimaLectura.valor }}
                    </span>
                    <span class="text-theme-sm text-gray-500 dark:text-gray-400">
                      {{ tipoSensor[medicion.tipo].unidad }}
                    </span>
                  </div>
                </div>

                <p
                  :class="[
                    'mt-1 text-theme-xs font-medium',
                    medicionEnAlerta(dispositivo, medicion)
                      ? 'text-error-600 dark:text-error-500'
                      : 'text-success-600 dark:text-success-500',
                  ]"
                >
                  {{
                    medicionEnAlerta(dispositivo, medicion)
                      ? 'Fuera del rango normal'
                      : 'Dentro del rango normal'
                  }}
                </p>

                <div class="mt-3">
                  <LecturaChart
                    :etiquetas="etiquetasGrafico"
                    :datos="datosDe(medicion)"
                    :unidad="tipoSensor[medicion.tipo].unidad"
                    :min="medicion.rangoNormal.min"
                    :max="medicion.rangoNormal.max"
                    :serie="tipoSensor[medicion.tipo].label"
                    :altura="260"
                  />
                </div>
              </section>
            </div>
          </div>
        </div>

        <div class="col-span-12 xl:col-span-4">
          <div
            class="h-full rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
          >
            <div class="px-6 py-5">
              <h3 class="text-base font-medium text-gray-800 dark:text-white/90">Ficha técnica</h3>
            </div>
            <div class="space-y-0 border-t border-gray-100 px-6 py-4 dark:border-gray-800">
              <div
                v-for="fila in fichaTecnica"
                :key="fila.etiqueta"
                class="flex items-center justify-between gap-4 border-b border-gray-100 py-2.5 last:border-0 dark:border-gray-800"
              >
                <span class="text-theme-sm text-gray-500 dark:text-gray-400">
                  {{ fila.etiqueta }}
                </span>
                <span
                  :class="[
                    'text-end text-theme-sm font-medium',
                    fila.alerta
                      ? 'text-warning-600 dark:text-orange-400'
                      : 'text-gray-800 dark:text-white/90',
                  ]"
                >
                  {{ fila.valor }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-12 gap-4 md:gap-6">
        <div class="col-span-12 xl:col-span-5">
          <div
            class="h-full rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
          >
            <div class="px-6 py-5">
              <h3 class="text-base font-medium text-gray-800 dark:text-white/90">Ubicación</h3>
            </div>
            <div class="space-y-0 border-t border-gray-100 px-6 py-4 dark:border-gray-800">
              <div
                v-for="fila in ubicacion"
                :key="fila.etiqueta"
                class="flex items-center justify-between gap-4 border-b border-gray-100 py-2.5 last:border-0 dark:border-gray-800"
              >
                <span class="text-theme-sm text-gray-500 dark:text-gray-400">
                  {{ fila.etiqueta }}
                </span>
                <span class="text-end text-theme-sm font-medium text-gray-800 dark:text-white/90">
                  {{ fila.valor }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="col-span-12 xl:col-span-7">
          <div
            class="h-full rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
          >
            <div class="px-6 py-5">
              <h3 class="text-base font-medium text-gray-800 dark:text-white/90">
                Historial de revisiones
              </h3>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {{ dispositivo.revisiones.length }} intervenciones registradas
              </p>
            </div>

            <ul class="border-t border-gray-100 px-6 py-4 dark:border-gray-800">
              <li
                v-for="(revision, index) in dispositivo.revisiones"
                :key="revision.fecha"
                :class="[
                  'relative border-s border-gray-200 ps-6 dark:border-gray-800',
                  index === dispositivo.revisiones.length - 1 ? 'pb-0' : 'pb-5',
                ]"
              >
                <span
                  class="absolute -start-[5px] top-1.5 h-2.5 w-2.5 rounded-full bg-brand-500 ring-4 ring-white dark:ring-gray-900"
                ></span>
                <p class="text-theme-sm font-medium text-gray-800 dark:text-white/90">
                  {{ revision.detalle }}
                </p>
                <p class="mt-0.5 text-theme-xs text-gray-500 dark:text-gray-400">
                  {{ formatoFecha(revision.fecha) }} · {{ revision.tecnico }}
                </p>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div
      v-else
      class="rounded-2xl border border-gray-200 bg-white px-6 py-12 text-center dark:border-gray-800 dark:bg-white/[0.03]"
    >
      <p class="text-title-md font-semibold text-gray-800 dark:text-white/90">
        No encontramos ese dispositivo
      </p>
      <p class="mt-2 text-theme-sm text-gray-500 dark:text-gray-400">
        El identificador no corresponde a ningún dispositivo registrado.
      </p>
      <router-link
        to="/sensores"
        class="mt-4 inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
      >
        Volver al listado
      </router-link>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import EstadoSensor from '@/components/sensores/EstadoSensor.vue'
import LecturaChart from '@/components/sensores/LecturaChart.vue'
import ChevronRightIcon from '@/icons/ChevronRightIcon.vue'
import {
  bombaEstado,
  diasDesde,
  dispositivoPorId,
  enAlerta,
  etiquetas24h,
  etiquetas7d,
  fechaUltimaLectura,
  formatoFecha,
  formatoFechaHora,
  formatoHora,
  medicionEnAlerta,
  plantacionPorId,
  revisionVencida,
  sectorPorId,
  tanquePorId,
  tipoSensor,
  type Medicion,
} from '@/data/mockSensores'

const route = useRoute()

const dispositivo = computed(() => dispositivoPorId(String(route.params.id)))
const rangoGrafico = ref<'24h' | 'd7'>('24h')

const rangosGrafico = [
  { valor: '24h' as const, etiqueta: 'Últimas 24 h' },
  { valor: 'd7' as const, etiqueta: 'Últimos 7 días' },
]

const etiquetasGrafico = computed(() => (rangoGrafico.value === '24h' ? etiquetas24h : etiquetas7d))

const etiquetasMediciones = computed(() =>
  (dispositivo.value?.mediciones ?? [])
    .map((medicion) => tipoSensor[medicion.tipo].label)
    .join(' · '),
)

const ubicacionDispositivo = computed(() => {
  const actual = dispositivo.value
  if (!actual) return ''
  const sector = sectorPorId(actual.sectorId)
  return sector?.nombre || sector?.invernadero || '—'
})

function datosDe(medicion: Medicion) {
  return rangoGrafico.value === '24h' ? medicion.serie24h : medicion.serie7d
}

const fichaTecnica = computed(() => {
  const actual = dispositivo.value
  if (!actual) return []
  return [
    { etiqueta: 'Código', valor: actual.codigo },
    { etiqueta: 'Mediciones', valor: etiquetasMediciones.value },
    { etiqueta: 'Firmware', valor: actual.firmware },
    { etiqueta: 'Instalado el', valor: formatoFecha(actual.instalado) },
    {
      etiqueta: 'Última lectura',
      valor: formatoFechaHora(fechaUltimaLectura(actual)),
    },
    {
      etiqueta: 'Última revisión',
      valor: `${formatoFecha(actual.ultimaRevision)} · ${actual.tecnicoRevision}`,
    },
    {
      etiqueta: 'Próxima revisión',
      valor: `${formatoFecha(actual.proximaRevision)}${revisionVencida(actual) ? ' · vencida' : ''}`,
      alerta: revisionVencida(actual),
    },
  ]
})

const ubicacion = computed(() => {
  const actual = dispositivo.value
  if (!actual) return []
  const sector = sectorPorId(actual.sectorId)
  const plantacion = plantacionPorId(actual.plantacionId)
  const tanque = actual.tanqueId ? tanquePorId(actual.tanqueId) : undefined
  const filasTanque = tanque
    ? [
        {
          etiqueta: 'Tanque',
          valor: `${tanque.nombre} · ${tanque.cama} · ${tanque.capacidadLitros.toLocaleString('es-AR')} L`,
        },
        { etiqueta: 'Bomba de agua', valor: bombaEstado[tanque.bomba].label },
      ]
    : []
  return [
    { etiqueta: 'Invernadero', valor: sector?.invernadero || '—' },
    { etiqueta: 'Sector', valor: sector?.nombre || '—' },
    { etiqueta: 'Superficie', valor: sector?.superficie || '—' },
    {
      etiqueta: 'Plantación',
      valor: plantacion ? `${plantacion.cultivo} · var. ${plantacion.variedad}` : '—',
    },
    {
      etiqueta: 'Siembra',
      valor: plantacion
        ? `${formatoFecha(plantacion.fechaSiembra)} · ${diasDesde(plantacion.fechaSiembra)} días de ciclo`
        : '—',
    },
    ...filasTanque,
    { etiqueta: 'Ubicación exacta', valor: actual.ubicacionDetalle },
  ]
})

function claseBateria(bateria: number) {
  if (bateria <= 20) return 'text-error-600 dark:text-error-500'
  if (bateria <= 50) return 'text-warning-600 dark:text-orange-400'
  return 'text-gray-800 dark:text-white/90'
}

function claseBarra(bateria: number) {
  if (bateria <= 20) return 'bg-error-500'
  if (bateria <= 50) return 'bg-warning-500'
  return 'bg-success-500'
}
</script>
