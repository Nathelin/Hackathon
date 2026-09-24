<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="Sensores" />

    <div class="space-y-5 sm:space-y-6">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5 md:gap-6">
        <div
          v-for="kpi in kpis"
          :key="kpi.etiqueta"
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6"
        >
          <div class="flex items-center justify-between gap-3">
            <p class="text-theme-sm text-gray-500 dark:text-gray-400">{{ kpi.etiqueta }}</p>
            <span :class="['h-2.5 w-2.5 rounded-full', puntosTono[kpi.tono]]"></span>
          </div>
          <h4 class="mt-2 text-title-lg font-bold text-gray-800 dark:text-white/90">
            {{ kpi.valor }}
          </h4>
          <p class="mt-1 text-theme-xs text-gray-500 dark:text-gray-400">{{ kpi.nota }}</p>
        </div>
      </div>

      <div
        class="rounded-2xl border border-gray-200 bg-white px-4 pb-4 pt-4 dark:border-gray-800 dark:bg-white/[0.03] sm:px-6"
      >
        <div class="flex flex-col gap-3 mb-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
              Inventario de dispositivos
            </h3>
            <p class="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">
              {{ dispositivosFiltrados.length }} de {{ dispositivos.length }} dispositivos ·
              {{ totalMediciones }} mediciones en total
            </p>
          </div>

          <button
            v-if="hayFiltros"
            type="button"
            class="inline-flex items-center gap-2 self-start rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-theme-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 hover:text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/[0.03] dark:hover:text-gray-200"
            @click="limpiarFiltros"
          >
            Limpiar filtros
          </button>
        </div>

        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div class="relative w-full sm:max-w-xs">
            <input
              v-model="busqueda"
              type="search"
              placeholder="Buscar código, nombre o ubicación"
              class="h-10 w-full rounded-lg border border-gray-200 bg-transparent py-2.5 ps-9 pe-4 text-theme-sm text-gray-800 placeholder:text-gray-400 focus:border-brand-300 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-white/90 dark:placeholder:text-gray-500 dark:focus:border-brand-300"
            />
            <svg
              class="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400 dark:text-gray-500"
              viewBox="0 0 20 20"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M17.5 17.5L14.5834 14.5833M16.6667 9.16667C16.6667 13.3089 13.3089 16.6667 9.16667 16.6667C5.02439 16.6667 1.66667 13.3089 1.66667 9.16667C1.66667 5.02439 5.02439 1.66667 9.16667 1.66667C13.3089 1.66667 16.6667 5.02439 16.6667 9.16667Z"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </div>

          <div class="relative w-full sm:w-56">
            <select
              v-model="filtroSector"
              class="h-10 w-full appearance-none rounded-lg border border-gray-200 bg-white py-2.5 ps-4 pe-10 text-theme-sm text-gray-700 shadow-theme-xs focus:border-brand-300 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400"
            >
              <option value="">Todos los sectores</option>
              <option v-for="sector in sectores" :key="sector.id" :value="sector.id">
                {{ sector.nombre || sector.invernadero }}
              </option>
            </select>
            <ChevronDownIcon
              class="pointer-events-none absolute end-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400 dark:text-gray-500"
            />
          </div>

          <div class="relative w-full sm:w-52">
            <select
              v-model="filtroEstado"
              class="h-10 w-full appearance-none rounded-lg border border-gray-200 bg-white py-2.5 ps-4 pe-10 text-theme-sm text-gray-700 shadow-theme-xs focus:border-brand-300 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400"
            >
              <option value="">Todos los estados</option>
              <option v-for="(meta, clave) in estadoSensor" :key="clave" :value="clave">
                {{ meta.label }}
              </option>
            </select>
            <ChevronDownIcon
              class="pointer-events-none absolute end-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400 dark:text-gray-500"
            />
          </div>
        </div>
      </div>

      <template v-if="grupos.length > 0">
        <section
          v-for="grupo in grupos"
          :key="grupo.sector.id"
          class="overflow-hidden rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
        >
          <div
            class="border-b border-gray-100 px-4 py-4 dark:border-gray-800 sm:px-6 bg-blue-100 dark:bg-blue-950"
          >
            <div class="flex flex-wrap items-center justify-between gap-x-3 gap-y-2">
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-base font-semibold text-gray-800 dark:text-white/90">
                  {{ grupo.sector.nombre || grupo.sector.invernadero }}
                </h3>
                <span
                  class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-theme-xs font-medium text-gray-700 dark:bg-white/5 dark:text-white/80"
                >
                  {{ grupo.dispositivos.length }} dispositivos
                </span>
              </div>

              <div class="flex flex-wrap items-center gap-1.5">
                <span
                  v-for="chip in resumenSector(grupo)"
                  :key="chip.etiqueta"
                  :class="[chipBase, chipClase[chip.tono]]"
                >
                  {{ chip.valor }} {{ chip.etiqueta }}
                </span>
              </div>
            </div>

            <div
              class="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-theme-xs text-gray-500 dark:text-gray-400"
            >
              <span>{{ grupo.sector.invernadero }} · {{ grupo.sector.superficie }}</span>
              <span v-for="info in plantacionesTexto(grupo)" :key="info">
                <span class="text-gray-300 dark:text-gray-600">·</span> {{ info }}
              </span>
            </div>
          </div>

          <div class="max-w-full overflow-x-auto custom-scrollbar">
            <table class="min-w-full">
              <thead>
                <tr class="border-b border-gray-100 dark:border-gray-800">
                  <th
                    v-for="columna in columnas"
                    :key="columna"
                    class="px-4 py-3 text-start sm:px-6"
                  >
                    <p class="font-medium text-gray-500 text-theme-xs dark:text-gray-400">
                      {{ columna }}
                    </p>
                  </th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="dispositivo in grupo.dispositivos"
                  :key="dispositivo.id"
                  class="cursor-pointer border-b border-gray-100 transition last:border-0 hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-white/[0.02]"
                  @click="irAlDetalle(dispositivo.id)"
                >
                  <td class="py-3 ps-4 pe-4 sm:ps-6">
                    <router-link
                      :to="{ name: 'SensorDetalle', params: { id: dispositivo.id } }"
                      class="block"
                      @click.stop
                    >
                      <p class="text-theme-sm font-medium text-gray-800 dark:text-white/90">
                        {{ dispositivo.codigo }}
                        <span class="font-normal text-gray-500 dark:text-gray-400">
                          · {{ dispositivo.nombre }}
                        </span>
                      </p>
                      <span class="text-theme-xs text-gray-500 dark:text-gray-400">
                        {{ etiquetasMediciones(dispositivo) }}
                      </span>
                    </router-link>
                  </td>

                  <td class="py-3 pe-4 whitespace-nowrap">
                    <p class="text-theme-sm text-gray-500 dark:text-gray-400">
                      {{ dispositivo.ubicacionDetalle }}
                    </p>
                  </td>

                  <td class="py-3 pe-4 whitespace-nowrap">
                    <p class="text-theme-sm text-gray-800 dark:text-white/90">
                      {{ formatoFecha(dispositivo.ultimaRevision) }}
                    </p>
                    <span class="text-theme-xs text-gray-500 dark:text-gray-400">
                      {{ dispositivo.tecnicoRevision }}
                    </span>
                    <p
                      :class="[
                        'mt-0.5 text-theme-xs',
                        revisionVencida(dispositivo)
                          ? 'font-medium text-warning-600 dark:text-orange-400'
                          : 'text-gray-500 dark:text-gray-400',
                      ]"
                    >
                      Próx. {{ formatoFecha(dispositivo.proximaRevision)
                      }}{{ revisionVencida(dispositivo) ? ' · vencida' : '' }}
                    </p>
                  </td>

                  <td class="py-3 pe-4 sm:pe-6">
                    <div class="flex items-center justify-between gap-3">
                      <EstadoSensor :estado="dispositivo.estado" :alerta="enAlerta(dispositivo)" />
                      <ChevronRightIcon class="h-4 w-4 shrink-0 text-gray-400 rtl:rotate-180" />
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>

      <div
        v-else
        class="rounded-2xl border border-gray-200 bg-white px-6 py-12 text-center dark:border-gray-800 dark:bg-white/[0.03]"
      >
        <p class="text-theme-base font-medium text-gray-800 dark:text-white/90">
          No hay dispositivos que coincidan con los filtros.
        </p>
        <button
          type="button"
          class="mt-3 text-theme-sm font-medium text-brand-500 hover:text-brand-600"
          @click="limpiarFiltros"
        >
          Limpiar filtros
        </button>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import EstadoSensor from '@/components/sensores/EstadoSensor.vue'
import ChevronDownIcon from '@/icons/ChevronDownIcon.vue'
import ChevronRightIcon from '@/icons/ChevronRightIcon.vue'
import {
  diasDesde,
  dispositivos,
  enAlerta,
  estadoSensor,
  formatoFecha,
  revisionVencida,
  sectores,
  tipoSensor,
  plantaciones,
  type Dispositivo,
} from '@/data/mockSensores'

const router = useRouter()

const busqueda = ref('')
const filtroSector = ref('')
const filtroEstado = ref('')

const columnas = ['Dispositivo', 'Ubicación', 'Última revisión', 'Estado']

const totalMediciones = computed(() =>
  dispositivos.reduce((total, dispositivo) => total + dispositivo.mediciones.length, 0),
)

const kpis = computed(() => [
  {
    etiqueta: 'Dispositivos totales',
    valor: dispositivos.length,
    nota: `${sectores.length} sectores · ${totalMediciones.value} mediciones`,
    tono: 'brand',
  },
  {
    etiqueta: 'Operativos',
    valor: dispositivos.filter((dispositivo) => dispositivo.estado === 'operativo').length,
    nota: 'con lectura activa',
    tono: 'success',
  },
  {
    etiqueta: 'Requieren revisión',
    valor: dispositivos.filter((dispositivo) => dispositivo.estado === 'revision').length,
    nota: 'con mantenimiento vencido',
    tono: 'warning',
  },
  {
    etiqueta: 'Sin conexión',
    valor: dispositivos.filter((dispositivo) => dispositivo.estado === 'sin_conexion').length,
    nota: 'sin reportar señal',
    tono: 'info',
  },
  {
    etiqueta: 'Alertas de umbral',
    valor: dispositivos.filter((dispositivo) => enAlerta(dispositivo)).length,
    nota: 'alguna medición fuera de rango',
    tono: 'error',
  },
])

const puntosTono: Record<string, string> = {
  brand: 'bg-brand-500',
  success: 'bg-success-500',
  warning: 'bg-warning-500',
  info: 'bg-blue-light-500',
  error: 'bg-error-500',
}

const chipBase = 'inline-flex items-center rounded-full px-2 py-0.5 text-theme-xs font-medium'

const chipClase: Record<string, string> = {
  success: 'bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-500',
  warning: 'bg-warning-50 text-warning-600 dark:bg-warning-500/15 dark:text-orange-400',
  info: 'bg-blue-light-50 text-blue-light-500 dark:bg-blue-light-500/15 dark:text-blue-light-500',
  error: 'bg-error-50 text-error-600 dark:bg-error-500/15 dark:text-error-500',
}

const hayFiltros = computed(
  () => busqueda.value.trim() !== '' || filtroSector.value !== '' || filtroEstado.value !== '',
)

const dispositivosFiltrados = computed(() => {
  const texto = busqueda.value.trim().toLowerCase()
  return dispositivos.filter((dispositivo) => {
    const coincideSector = filtroSector.value === '' || dispositivo.sectorId === filtroSector.value
    const coincideEstado = filtroEstado.value === '' || dispositivo.estado === filtroEstado.value
    const textoDispositivo = `${dispositivo.codigo} ${dispositivo.nombre} ${
      dispositivo.ubicacionDetalle
    } ${dispositivo.mediciones.map((medicion) => tipoSensor[medicion.tipo].label).join(' ')}`
    const coincideTexto = texto === '' || textoDispositivo.toLowerCase().includes(texto)
    return coincideSector && coincideEstado && coincideTexto
  })
})

type GrupoSector = {
  sector: (typeof sectores)[number]
  plantaciones: typeof plantaciones
  dispositivos: Dispositivo[]
}

const grupos = computed<GrupoSector[]>(() =>
  sectores
    .map((sector) => ({
      sector,
      plantaciones: plantaciones.filter((plantacion) => plantacion.sectorId === sector.id),
      dispositivos: dispositivosFiltrados.value.filter(
        (dispositivo) => dispositivo.sectorId === sector.id,
      ),
    }))
    .filter((grupo) => grupo.dispositivos.length > 0),
)

function etiquetasMediciones(dispositivo: Dispositivo) {
  return dispositivo.mediciones.map((medicion) => tipoSensor[medicion.tipo].label).join(' · ')
}

function resumenSector(grupo: GrupoSector) {
  const contar = (estado: Dispositivo['estado']) =>
    grupo.dispositivos.filter((dispositivo) => dispositivo.estado === estado).length
  const alertas = grupo.dispositivos.filter((dispositivo) => enAlerta(dispositivo)).length

  return [
    { etiqueta: 'operativos', valor: contar('operativo'), tono: 'success' },
    { etiqueta: 'requieren revisión', valor: contar('revision'), tono: 'warning' },
    { etiqueta: 'sin conexión', valor: contar('sin_conexion'), tono: 'info' },
    { etiqueta: 'fuera de servicio', valor: contar('fuera_servicio'), tono: 'error' },
    {
      etiqueta: alertas === 1 ? 'alerta de umbral' : 'alertas de umbral',
      valor: alertas,
      tono: 'error',
    },
  ].filter((chip) => chip.valor > 0)
}

function plantacionesTexto(grupo: GrupoSector) {
  return grupo.plantaciones.map(
    (plantacion) =>
      `${plantacion.cultivo} · siembra ${formatoFecha(
        plantacion.fechaSiembra,
      )} (${diasDesde(plantacion.fechaSiembra)} días de ciclo)`,
  )
}

function limpiarFiltros() {
  busqueda.value = ''
  filtroSector.value = ''
  filtroEstado.value = ''
}

function irAlDetalle(id: string) {
  router.push({ name: 'SensorDetalle', params: { id } })
}
</script>
