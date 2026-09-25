<template>
  <AdminLayout>
    <h1 class="font-medium text-4xl pb-5">¡Bienvenido!</h1>
    <h2 class="font-medium text-2xl pb-5">Resumen general de tus invernaderos.</h2>

    <div class="space-y-5 pb-6 sm:space-y-6">
      <div
        v-if="anomalias.length > 0"
        class="rounded-2xl border border-error-500/30 bg-error-50 p-4 dark:bg-error-500/10 sm:p-6"
      >
        <div class="flex items-start gap-3">
          <span
            class="mt-0.5 inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-error-100 text-error-600 dark:bg-error-500/20 dark:text-error-500"
          >
            <WarningIcon class="h-5 w-5" />
          </span>
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center justify-between gap-x-3 gap-y-2">
              <div>
                <h3 class="text-base font-semibold text-error-700 dark:text-error-400">
                  {{ anomalias.length }}
                  {{ anomalias.length === 1 ? 'anomalía detectada' : 'anomalías detectadas' }}
                </h3>
                <p class="mt-0.5 text-theme-sm text-error-600 dark:text-error-400">
                  Algunas lecturas requieren tu atención.
                </p>
              </div>
              <span
                class="rounded-full bg-error-100 px-2.5 py-1 text-theme-xs font-medium text-error-700 dark:bg-error-500/20 dark:text-error-400"
              >
                {{ errores }} críticas · {{ avisos }} avisos
              </span>
            </div>

            <ul class="mt-3 divide-y divide-error-100 dark:divide-error-500/15">
              <li v-for="(anomalia, indice) in anomalias" :key="indice">
                <router-link :to="anomalia.href" class="group flex items-center gap-3 py-2.5">
                  <span
                    :class="[
                      'h-2 w-2 shrink-0 rounded-full',
                      anomalia.tono === 'error' ? 'bg-error-500' : 'bg-warning-500',
                    ]"
                  />
                  <span class="min-w-0 flex-1">
                    <span class="flex flex-wrap items-baseline gap-x-2">
                      <span class="text-theme-sm font-medium text-gray-800 dark:text-white/90">
                        {{ anomalia.titulo }}
                      </span>
                      <span class="text-theme-xs text-gray-500 dark:text-gray-400">
                        {{ anomalia.ubicacion }}
                      </span>
                    </span>
                    <span class="block text-theme-xs text-gray-500 dark:text-gray-400">
                      {{ anomalia.detalle }}
                    </span>
                  </span>
                  <ChevronRightIcon
                    class="h-4 w-4 shrink-0 text-gray-400 group-hover:text-brand-500 rtl:rotate-180"
                  />
                </router-link>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div
        v-else
        class="flex items-center gap-3 rounded-2xl border border-success-500/30 bg-success-50 p-4 dark:bg-success-500/10 sm:p-6"
      >
        <span
          class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-success-100 text-success-600 dark:bg-success-500/20 dark:text-success-500"
        >
          <SuccessIcon class="h-5 w-5" />
        </span>
        <div>
          <h3 class="text-base font-semibold text-success-700 dark:text-success-400">
            Sin anomalías
          </h3>
          <p class="mt-0.5 text-theme-sm text-success-600 dark:text-success-400">
            Todas las lecturas están dentro de su rango esperado.
          </p>
        </div>
      </div>

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

      <div class="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <section
          v-for="vista in vistas"
          :key="vista.nombre"
          class="overflow-hidden rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
        >
          <div class="border-b border-gray-100 px-4 py-4 dark:border-gray-800 sm:px-6">
            <div class="flex flex-wrap items-center justify-between gap-x-3 gap-y-2">
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-base font-semibold text-gray-800 dark:text-white/90">
                  {{ vista.nombre }}
                </h3>
                <span
                  class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-theme-xs font-medium text-gray-700 dark:bg-white/5 dark:text-white/80"
                >
                  {{ vista.dispositivos.length }} dispositivos
                </span>
                <span :class="[chipBase, chipClase.success]">
                  {{ vista.operativos }} operativos
                </span>
                <span v-if="vista.anomalias > 0" :class="[chipBase, chipClase.error]">
                  {{ vista.anomalias }}
                  {{ vista.anomalias === 1 ? 'anomalía' : 'anomalías' }}
                </span>
              </div>

              <router-link
                v-if="vista.ruta"
                :to="vista.ruta"
                class="inline-flex items-center gap-1 text-theme-sm font-medium text-brand-500 hover:text-brand-600"
              >
                Ver invernadero
                <ChevronRightIcon class="h-4 w-4 rtl:rotate-180" />
              </router-link>
            </div>

            <p
              v-if="vista.plantaciones.length > 0"
              class="mt-1.5 text-theme-xs text-gray-500 dark:text-gray-400"
            >
              {{ vista.plantaciones.join(' · ') }}
            </p>
          </div>

          <div class="px-4 py-4 sm:px-6">
            <div class="grid grid-cols-2 gap-3">
              <div
                v-for="lectura in vista.ambiente"
                :key="lectura.titulo"
                class="rounded-xl border border-gray-100 bg-gray-50 p-3 dark:border-gray-800 dark:bg-white/[0.02]"
              >
                <p class="text-theme-xs text-gray-500 dark:text-gray-400">{{ lectura.titulo }}</p>
                <p
                  :class="[
                    'mt-1 text-title-lg font-bold',
                    lectura.alerta
                      ? 'text-error-600 dark:text-error-500'
                      : 'text-gray-800 dark:text-white/90',
                  ]"
                >
                  {{ lectura.valor
                  }}<span class="ms-1 text-theme-sm font-medium">{{ lectura.unidad }}</span>
                </p>
                <p class="text-theme-xs text-gray-500 dark:text-gray-400">
                  Lectura {{ lectura.hora }}
                </p>
              </div>
            </div>

            <div class="mt-4 divide-y divide-gray-100 dark:divide-gray-800">
              <div
                v-for="fila in vista.tanques"
                :key="fila.tanque.id"
                class="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 py-3"
              >
                <div class="min-w-0">
                  <p class="text-theme-sm font-medium text-gray-800 dark:text-white/90">
                    {{ fila.tanque.nombre }}
                  </p>
                  <p class="text-theme-xs text-gray-500 dark:text-gray-400">
                    {{ fila.tanque.cama }} · {{ fila.tanque.capacidadLitros }} L
                  </p>
                </div>

                <div class="flex items-center gap-4 sm:gap-6">
                  <div class="text-end">
                    <p class="text-theme-xs text-gray-500 dark:text-gray-400">pH</p>
                    <p
                      :class="[
                        'text-theme-sm font-semibold',
                        fila.phAlerta
                          ? 'text-error-600 dark:text-error-500'
                          : 'text-gray-800 dark:text-white/90',
                      ]"
                    >
                      {{ fila.ph ? fila.ph.ultimaLectura.valor : '—' }}
                    </p>
                  </div>

                  <div class="text-end">
                    <p class="text-theme-xs text-gray-500 dark:text-gray-400">EC</p>
                    <p
                      :class="[
                        'text-theme-sm font-semibold',
                        fila.ecAlerta
                          ? 'text-error-600 dark:text-error-500'
                          : 'text-gray-800 dark:text-white/90',
                      ]"
                    >
                      {{ fila.ec ? fila.ec.ultimaLectura.valor : '—'
                      }}<span
                        v-if="fila.ec"
                        class="ms-1 text-theme-xs font-normal text-gray-500 dark:text-gray-400"
                        >mS/cm</span
                      >
                    </p>
                  </div>

                  <div class="text-end">
                    <p class="text-theme-xs text-gray-500 dark:text-gray-400">Nivel</p>
                    <p
                      :class="[
                        'text-theme-sm font-semibold',
                        fila.nivelAlerta
                          ? 'text-error-600 dark:text-error-500'
                          : 'text-gray-800 dark:text-white/90',
                      ]"
                    >
                      {{ fila.nivel ? `${fila.nivel.ultimaLectura.valor}%` : '—' }}
                    </p>
                  </div>

                  <span :class="[chipBase, chipClase[bombaEstado[fila.tanque.bomba].color]]">
                    {{ bombaEstado[fila.tanque.bomba].label }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div
        class="overflow-hidden rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
      >
        <div class="border-b border-gray-100 px-4 py-4 dark:border-gray-800 sm:px-6">
          <div class="flex flex-wrap items-center justify-between gap-x-3 gap-y-2">
            <h3 class="text-base font-semibold text-gray-800 dark:text-white/90">
              Últimas lecturas
            </h3>
            <span
              class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-theme-xs font-medium text-gray-700 dark:bg-white/5 dark:text-white/80"
            >
              {{ totalLecturas }} lecturas · {{ formatoFecha(hoy) }}
            </span>
          </div>
        </div>

        <div class="max-w-full overflow-x-auto custom-scrollbar">
          <table class="min-w-[720px]">
            <thead>
              <tr class="border-b border-gray-100 dark:border-gray-800">
                <th v-for="columna in columnas" :key="columna" class="px-4 py-3 text-start sm:px-6">
                  <p class="font-medium text-gray-500 text-theme-xs dark:text-gray-400">
                    {{ columna }}
                  </p>
                </th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="lectura in ultimasLecturas"
                :key="`${lectura.dispositivo.id}-${lectura.medicion.tipo}`"
                class="cursor-pointer border-b border-gray-100 transition last:border-0 hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-white/[0.02]"
                @click="irAlDetalle(lectura.dispositivo.id)"
              >
                <td class="py-3 ps-4 pe-4 whitespace-nowrap sm:ps-6">
                  <p class="text-theme-sm text-gray-800 dark:text-white/90">{{ lectura.hora }}</p>
                  <span class="text-theme-xs text-gray-500 dark:text-gray-400">
                    {{ formatoFecha(lectura.fecha) }}
                  </span>
                </td>

                <td class="py-3 pe-4">
                  <router-link
                    :to="{ name: 'SensorDetalle', params: { id: lectura.dispositivo.id } }"
                    class="block"
                    @click.stop
                  >
                    <p class="text-theme-sm font-medium text-gray-800 dark:text-white/90">
                      {{ lectura.dispositivo.codigo }}
                      <span class="font-normal text-gray-500 dark:text-gray-400">
                        · {{ lectura.dispositivo.nombre }}
                      </span>
                    </p>
                  </router-link>
                </td>

                <td class="py-3 pe-4 whitespace-nowrap">
                  <p class="text-theme-sm text-gray-500 dark:text-gray-400">
                    {{ lectura.ubicacion }}
                  </p>
                </td>

                <td class="py-3 pe-4 whitespace-nowrap">
                  <p class="text-theme-sm text-gray-800 dark:text-white/90">
                    {{ tipoSensor[lectura.medicion.tipo].label }}
                  </p>
                </td>

                <td class="py-3 pe-4 whitespace-nowrap sm:pe-6">
                  <p
                    :class="[
                      'text-theme-sm font-semibold',
                      lectura.alerta
                        ? 'text-error-600 dark:text-error-500'
                        : 'text-gray-800 dark:text-white/90',
                    ]"
                  >
                    {{ lectura.medicion.ultimaLectura.valor
                    }}<span
                      v-if="tipoSensor[lectura.medicion.tipo].unidad !== 'pH'"
                      class="ms-1 text-theme-xs font-normal text-gray-500 dark:text-gray-400"
                      >{{ tipoSensor[lectura.medicion.tipo].unidad }}</span
                    >
                  </p>
                  <span
                    v-if="lectura.alerta"
                    class="text-theme-xs text-error-600 dark:text-error-500"
                  >
                    fuera de rango
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import WarningIcon from '@/icons/WarningIcon.vue'
import SuccessIcon from '@/icons/SuccessIcon.vue'
import ChevronRightIcon from '@/icons/ChevronRightIcon.vue'
import {
  bombaEstado,
  diasDesde,
  dispositivoDelTanque,
  dispositivos,
  formatoFecha,
  formatoHora,
  hoy,
  medicionEnAlerta,
  medicionPorTipo,
  plantaciones,
  revisionVencida,
  sectorPorId,
  sectores,
  tanquePorId,
  tanques,
  tanquesDeInvernadero,
  tipoSensor,
  type Dispositivo,
  type Medicion,
  type Tanque,
} from '@/data/mockSensores'

const router = useRouter()

const columnas = ['Hora', 'Dispositivo', 'Ubicación', 'Lectura', 'Valor']

const rutasInvernadero: Record<string, string> = {
  'Invernadero 1': '/invernadero1',
  'Invernadero 2': '/invernadero2',
}

const metricasAmbiente = [
  { tipo: 'temperatura', titulo: 'Temperatura' },
  { tipo: 'humedad_aire', titulo: 'Humedad' },
] as const

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

const nombresInvernaderos = computed(() => {
  const conTanque = new Set(
    tanques.map((tanque) => sectorPorId(tanque.sectorId)?.invernadero ?? ''),
  )
  const nombres = sectores.map((sector) => sector.invernadero)
  return nombres.filter(
    (nombre, indice) => nombres.indexOf(nombre) === indice && conTanque.has(nombre),
  )
})

const dispositivosInvernadero = computed(() =>
  dispositivos.filter((dispositivo) =>
    nombresInvernaderos.value.includes(sectorPorId(dispositivo.sectorId)?.invernadero ?? ''),
  ),
)

type Anomalia = {
  tono: 'error' | 'warning'
  invernadero: string
  titulo: string
  detalle: string
  ubicacion: string
  href: string
}

function ubicacionDe(dispositivo: Dispositivo): string {
  const sector = sectorPorId(dispositivo.sectorId)
  const tanque = dispositivo.tanqueId ? tanquePorId(dispositivo.tanqueId) : undefined
  return [sector?.invernadero, tanque?.nombre ?? sector?.nombre ?? ''].filter(Boolean).join(' · ')
}

function unidadTexto(medicion: Medicion): string {
  const unidad = tipoSensor[medicion.tipo].unidad
  return unidad === 'pH' ? '' : ` ${unidad}`
}

const anomalias = computed<Anomalia[]>(() => {
  const lista: Anomalia[] = []

  for (const dispositivo of dispositivosInvernadero.value) {
    const sector = sectorPorId(dispositivo.sectorId)
    const invernadero = sector?.invernadero ?? ''
    const base = ubicacionDe(dispositivo)
    const ubicacion = `${base} · ${dispositivo.codigo}`
    const href = `/sensores/${dispositivo.id}`

    for (const medicion of dispositivo.mediciones) {
      if (!medicionEnAlerta(dispositivo, medicion)) continue
      const meta = tipoSensor[medicion.tipo]
      lista.push({
        tono: 'error',
        invernadero,
        titulo: `${meta.label} fuera de rango`,
        detalle: `${medicion.ultimaLectura.valor}${unidadTexto(medicion)} · rango esperado ${medicion.rangoNormal.min}–${medicion.rangoNormal.max}${unidadTexto(medicion)}`,
        ubicacion,
        href,
      })
    }

    if (dispositivo.estado === 'sin_conexion') {
      lista.push({
        tono: 'error',
        invernadero,
        titulo: 'Dispositivo sin conexión',
        detalle: `${dispositivo.codigo} no está reportando lecturas`,
        ubicacion,
        href,
      })
    }

    if (dispositivo.estado === 'fuera_servicio') {
      lista.push({
        tono: 'error',
        invernadero,
        titulo: 'Dispositivo fuera de servicio',
        detalle: `${dispositivo.codigo} no está operativo`,
        ubicacion,
        href,
      })
    }

    if (revisionVencida(dispositivo)) {
      lista.push({
        tono: 'warning',
        invernadero,
        titulo: 'Revisión vencida',
        detalle: `Próxima revisión: ${formatoFecha(dispositivo.proximaRevision)}`,
        ubicacion,
        href,
      })
    } else if (dispositivo.estado === 'revision') {
      lista.push({
        tono: 'warning',
        invernadero,
        titulo: 'Requiere revisión',
        detalle: 'Mantenimiento programado pendiente',
        ubicacion,
        href,
      })
    }

    if (dispositivo.bateria <= 20) {
      lista.push({
        tono: 'warning',
        invernadero,
        titulo: 'Batería baja',
        detalle: `${dispositivo.bateria}% de batería restante`,
        ubicacion,
        href,
      })
    }
  }

  for (const tanque of tanques) {
    if (tanque.bomba === 'operativa') continue
    const sector = sectorPorId(tanque.sectorId)
    const invernadero = sector?.invernadero ?? ''
    if (!nombresInvernaderos.value.includes(invernadero)) continue
    const enAlarma = tanque.bomba === 'alarma'
    lista.push({
      tono: enAlarma ? 'error' : 'warning',
      invernadero,
      titulo: enAlarma ? 'Bomba en alarma' : 'Bomba detenida',
      detalle: enAlarma
        ? `La bomba del ${tanque.nombre} reporta alarma de bombeo`
        : `La bomba del ${tanque.nombre} no está reponiendo agua`,
      ubicacion: `${invernadero} · ${tanque.nombre}`,
      href: `/sensores/${tanque.dispositivoId}`,
    })
  }

  return [
    ...lista.filter((anomalia) => anomalia.tono === 'error'),
    ...lista.filter((anomalia) => anomalia.tono === 'warning'),
  ]
})

const errores = computed(
  () => anomalias.value.filter((anomalia) => anomalia.tono === 'error').length,
)

const avisos = computed(
  () => anomalias.value.filter((anomalia) => anomalia.tono === 'warning').length,
)

const totalLecturas = computed(() =>
  dispositivosInvernadero.value.reduce(
    (total, dispositivo) => total + dispositivo.mediciones.length,
    0,
  ),
)

type LecturaReciente = {
  fecha: string
  hora: string
  dispositivo: Dispositivo
  ubicacion: string
  medicion: Medicion
  alerta: boolean
}

const ultimasLecturas = computed<LecturaReciente[]>(() =>
  dispositivosInvernadero.value
    .flatMap((dispositivo) =>
      dispositivo.mediciones.map((medicion) => ({
        fecha: medicion.ultimaLectura.fecha,
        hora: formatoHora(medicion.ultimaLectura.fecha),
        dispositivo,
        ubicacion: ubicacionDe(dispositivo),
        medicion,
        alerta: medicionEnAlerta(dispositivo, medicion),
      })),
    )
    .sort((a, b) => b.fecha.localeCompare(a.fecha))
    .slice(0, 8),
)

type LecturaAmbiente = {
  titulo: string
  valor: number
  unidad: string
  hora: string
  alerta: boolean
}

type FilaTanque = {
  tanque: Tanque
  ph?: Medicion
  ec?: Medicion
  nivel?: Medicion
  phAlerta: boolean
  ecAlerta: boolean
  nivelAlerta: boolean
}

type VistaInvernadero = {
  nombre: string
  ruta?: string
  dispositivos: Dispositivo[]
  operativos: number
  anomalias: number
  plantaciones: string[]
  ambiente: LecturaAmbiente[]
  tanques: FilaTanque[]
}

const vistas = computed<VistaInvernadero[]>(() =>
  nombresInvernaderos.value.map((nombre) => {
    const sectoresInvernadero = sectores.filter((sector) => sector.invernadero === nombre)
    const ids = new Set(sectoresInvernadero.map((sector) => sector.id))
    const propios = dispositivosInvernadero.value.filter((dispositivo) =>
      ids.has(dispositivo.sectorId),
    )

    const ambiente: LecturaAmbiente[] = []
    for (const metrica of metricasAmbiente) {
      const dispositivo = propios.find((item) => medicionPorTipo(item, metrica.tipo) !== undefined)
      const medicion = dispositivo ? medicionPorTipo(dispositivo, metrica.tipo) : undefined
      if (!dispositivo || !medicion) continue
      ambiente.push({
        titulo: metrica.titulo,
        valor: medicion.ultimaLectura.valor,
        unidad: tipoSensor[metrica.tipo].unidad,
        hora: formatoHora(medicion.ultimaLectura.fecha),
        alerta: medicionEnAlerta(dispositivo, medicion),
      })
    }

    const filas: FilaTanque[] = []
    for (const tanque of tanquesDeInvernadero(nombre)) {
      const dispositivo = dispositivoDelTanque(tanque)
      if (!dispositivo) continue
      const ph = medicionPorTipo(dispositivo, 'ph')
      const ec = medicionPorTipo(dispositivo, 'ec')
      const nivel = medicionPorTipo(dispositivo, 'nivel_tanque')
      filas.push({
        tanque,
        ph,
        ec,
        nivel,
        phAlerta: ph ? medicionEnAlerta(dispositivo, ph) : false,
        ecAlerta: ec ? medicionEnAlerta(dispositivo, ec) : false,
        nivelAlerta: nivel ? medicionEnAlerta(dispositivo, nivel) : false,
      })
    }

    return {
      nombre,
      ruta: rutasInvernadero[nombre],
      dispositivos: propios,
      operativos: propios.filter((dispositivo) => dispositivo.estado === 'operativo').length,
      anomalias: anomalias.value.filter((anomalia) => anomalia.invernadero === nombre).length,
      plantaciones: plantaciones
        .filter((plantacion) => ids.has(plantacion.sectorId))
        .map(
          (plantacion) =>
            `${plantacion.cultivo} · ${diasDesde(plantacion.fechaSiembra)} días de ciclo`,
        ),
      ambiente,
      tanques: filas,
    }
  }),
)

const operativos = computed(
  () =>
    dispositivosInvernadero.value.filter((dispositivo) => dispositivo.estado === 'operativo')
      .length,
)

const bombasOperativas = computed(
  () => tanques.filter((tanque) => tanque.bomba === 'operativa').length,
)

const ultimaLectura = computed(() => ultimasLecturas.value[0])

const kpis = computed(() => [
  {
    etiqueta: 'Invernaderos',
    valor: nombresInvernaderos.value.length,
    nota: `${tanques.length} tanques · ${dispositivosInvernadero.value.length} dispositivos`,
    tono: 'brand',
  },
  {
    etiqueta: 'Dispositivos operativos',
    valor: operativos.value,
    nota: `de ${dispositivosInvernadero.value.length} en monitoreo`,
    tono: 'success',
  },
  {
    etiqueta: 'Anomalías activas',
    valor: anomalias.value.length,
    nota:
      anomalias.value.length > 0
        ? `${errores.value} críticas · ${avisos.value} avisos`
        : 'todo en orden',
    tono: anomalias.value.length > 0 ? 'error' : 'success',
  },
  {
    etiqueta: 'Bombas operativas',
    valor: `${bombasOperativas.value}/${tanques.length}`,
    nota:
      bombasOperativas.value < tanques.length
        ? `${tanques.length - bombasOperativas.value} requieren atención`
        : 'sin novedades',
    tono: bombasOperativas.value < tanques.length ? 'warning' : 'success',
  },
  {
    etiqueta: 'Última lectura',
    valor: ultimaLectura.value?.hora ?? '—',
    nota: ultimaLectura.value ? formatoFecha(ultimaLectura.value.fecha) : 'sin lecturas',
    tono: 'info',
  },
])

function irAlDetalle(id: string) {
  router.push({ name: 'SensorDetalle', params: { id } })
}
</script>
