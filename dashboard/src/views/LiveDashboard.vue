<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="Invernadero 1" />
    <div class="space-y-6 pb-20 text-gray-800 dark:text-white/90">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div class="flex flex-wrap items-center gap-2.5" role="status" aria-live="polite">
            <span
              class="h-2.5 w-2.5 shrink-0 rounded-full"
              :class="connected ? 'bg-success-500' : 'bg-warning-500'"
            />
            <span class="min-w-0 break-words text-sm font-medium">{{ connectionText }}</span>
            <span class="text-xs text-gray-500 dark:text-gray-400">{{ lastSeen }}</span>
          </div>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Tanque 1 · Lechuga hidropónica · Simulación con 4 B10K
          </p>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div
          v-for="s in summaries"
          :key="s.label"
          class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
        >
          <p class="text-xs text-gray-500 dark:text-gray-400">{{ s.label }}</p>
          <p class="mt-1 text-2xl font-semibold">{{ s.value }}</p>
        </div>
      </div>

      <section
        class="grid min-w-0 grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4"
        aria-label="Lecturas en tiempo real"
      >
        <article
          v-for="key in keys"
          :key="key"
          class="min-w-0 rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
          :data-metric="key"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <h2 class="text-sm font-semibold leading-snug">{{ spec(key).label }}</h2>
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                {{
                  key === 'ph' || key === 'ec' ? 'Solución · Tanque 1' : 'Ambiente · Inv. 1'
                }}
              </p>
            </div>
            <span class="shrink-0 rounded-full px-2 py-1 text-xs font-medium" :class="badge(key)">{{
              connected ? labels[metric(key)?.level || 'safe'] : 'Sin datos actuales'
            }}</span>
          </div>
          <p class="mt-4 flex flex-wrap items-baseline gap-2">
            <strong class="text-3xl font-semibold tabular-nums 2xl:text-4xl">{{
              connected && metric(key) ? format(metric(key)!.value, key) : '—'
            }}</strong
            ><span class="text-sm text-gray-500 dark:text-gray-400">{{ spec(key).unit }}</span>
          </p>
          <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
            Objetivo {{ spec(key).normal[0] }}–{{ spec(key).normal[1] }} {{ spec(key).unit }}
          </p>
          <svg
            viewBox="0 0 300 90"
            class="mt-4 h-16 w-full overflow-hidden text-brand-500"
            role="img"
            :aria-label="`Evolución reciente de ${spec(key).label}`"
          >
            <rect
              x="0"
              :y="chartY(spec(key).normal[1], key)"
              width="300"
              :height="chartY(spec(key).normal[0], key) - chartY(spec(key).normal[1], key)"
              class="fill-success-500/10"
            />
            <polyline
              v-for="(line, i) in chartSegments(key)"
              :key="i"
              :points="line"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              vector-effect="non-scaling-stroke"
            />
          </svg>
          <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>Últimos 2 minutos</span><span>Ahora</span>
          </div>
          <p class="mt-3 text-sm leading-relaxed text-gray-600 dark:text-gray-300">
            {{
              connected
                ? metric(key)?.advice
                : 'Esperando una lectura nueva. Los valores anteriores no se evalúan como actuales.'
            }}
          </p>
          <details
            class="mt-3 border-t border-gray-100 pt-3 text-xs text-gray-500 dark:border-gray-800 dark:text-gray-400"
          >
            <summary class="cursor-pointer">Detalle de la simulación</summary>
            <p class="mt-2">
              GPIO {{ spec(key).pin }} · ADC {{ connected ? metric(key)?.raw : '—' }} / 4095
            </p>
            <p>Escala: {{ spec(key).minimum }}–{{ spec(key).maximum }} {{ spec(key).unit }}</p>
          </details>
        </article>
      </section>

      <div class="grid min-w-0 grid-cols-1 gap-5 xl:grid-cols-2">
        <ComponentCard
          title="Alertas del prototipo"
          desc="El aviso aparece apenas una lectura entra en nivel crítico. Se limita la repetición del mismo evento."
        >
          <button
            type="button"
            class="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            :disabled="permission === 'granted' || permission === 'unsupported'"
            @click="enableNotifications"
          >
            {{
              permission === 'granted'
                ? 'Notificaciones activadas'
                : permission === 'unsupported'
                  ? 'Navegador sin notificaciones'
                  : 'Activar notificaciones del navegador'
            }}
          </button>
          <p v-if="permission === 'denied'" class="text-sm text-warning-600 dark:text-warning-400">
            El navegador bloqueó los avisos. Podés habilitarlos en los permisos del sitio.
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            Avisos del navegador con la página abierta. Correo:
            {{
              data?.email_configured
                ? 'configurado'
                : 'pendiente de configurar SMTP y destinatario'
            }}.
          </p>
          <p v-if="!data?.alerts.length" class="text-sm text-gray-500 dark:text-gray-400">
            Todavía no hay alertas confirmadas en esta sesión.
          </p>
          <ul v-else class="max-h-72 space-y-3 overflow-y-auto" aria-live="polite">
            <li
              v-for="a in data.alerts.slice(0, 12)"
              :key="a.id"
              class="rounded-xl border border-error-200 bg-error-50 p-3 text-sm dark:border-error-500/30 dark:bg-error-500/10"
            >
              <p class="font-semibold">
                {{ a.label }} · {{ a.value }} {{ a.unit }}
                <span class="text-xs font-normal">{{
                  a.resolved ? '· recuperado' : '· alerta registrada'
                }}</span>
              </p>
              <p class="mt-1">{{ a.message }}</p>
              <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                {{ time(a.at) }} · Correo: {{ mailLabels[a.email] || a.email }}
              </p>
            </li>
          </ul>
        </ComponentCard>
        <ComponentCard
          title="Cómo interpretar los datos"
          :desc="data?.profile.name || 'Perfil de lechuga'"
        >
          <p class="text-sm leading-relaxed text-gray-600 dark:text-gray-300">
            Los potenciómetros representan sensores; no miden plantas. El análisis usa reglas de
            referencia para los avisos. El chat local explica los datos con textos predeterminados;
            ninguno constituye un diagnóstico del cultivo.
          </p>
          <div class="overflow-x-auto">
            <table class="w-full text-start text-xs">
              <caption class="mb-3 text-start font-medium">
                Umbrales críticos del prototipo
              </caption>
              <thead>
                <tr class="border-b border-gray-200 dark:border-gray-800">
                  <th class="py-2 text-start">Parámetro</th>
                  <th class="py-2 text-start">Avisar si</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="key in keys"
                  :key="key"
                  class="border-b border-gray-100 dark:border-gray-800"
                >
                  <td class="py-2">{{ spec(key).label }}</td>
                  <td class="py-2">
                    ≤ {{ spec(key).critical[0] }} o ≥ {{ spec(key).critical[1] }}
                    {{ spec(key).unit }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="text-xs leading-relaxed text-gray-500 dark:text-gray-400">
            {{ data?.profile.note }} Los gráficos y avisos se conservan sólo en memoria; no hay
            histórico persistente. Nivel de agua y bomba: sin sensores conectados.
          </p>
          <ul class="space-y-2 text-xs text-brand-600 dark:text-brand-400">
            <li v-for="source in data?.profile.sources" :key="source.url">
              <a :href="source.url" target="_blank" rel="noopener noreferrer" class="underline"
                >{{ source.title }} ↗</a
              >
            </li>
          </ul>
        </ComponentCard>
      </div>
    </div>
    <button
      type="button"
      class="fixed bottom-5 end-5 z-40 inline-flex items-center gap-2 rounded-full bg-brand-500 px-4 py-3 text-sm font-semibold text-white shadow-theme-lg transition hover:bg-brand-600 focus:outline-none focus:ring-4 focus:ring-brand-500/20 sm:px-5"
      aria-label="Consultar al asistente sobre las lecturas"
      @click="chatOpen = true"
    >
      <svg
        viewBox="0 0 24 24"
        class="h-5 w-5"
        fill="none"
        stroke="currentColor"
        stroke-width="1.9"
        aria-hidden="true"
      >
        <path d="M8 18.5 4 21v-5a8 8 0 1 1 4 2.5Z" stroke-linecap="round" stroke-linejoin="round" />
        <path
          d="M8.5 10.5h.01M12 10.5h.01M15.5 10.5h.01"
          stroke-linecap="round"
          stroke-width="2.5"
        />
      </svg>
      <span>Consultar al asistente</span>
    </button>
    <AnalysisChat :open="chatOpen" @close="chatOpen = false" />
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import AnalysisChat from '@/components/telemetry/AnalysisChat.vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import ComponentCard from '@/components/common/ComponentCard.vue'
import { useTelemetry, type MetricKey, type Spec } from '@/composables/useTelemetry'
const { data, connected, connectionText, permission, enableNotifications, now } = useTelemetry()
const chatOpen = ref(false)
const keys: MetricKey[] = ['ph', 'ec', 'temperature', 'humidity']
const labels = { safe: 'Bien', warning: 'Atención', critical: 'Crítico' }
const mailLabels: Record<string, string> = {
  disabled: 'no configurado',
  queued: 'en cola',
  sent: 'enviado',
  failed: 'falló el envío',
}
const fallback: Record<MetricKey, Spec> = {
  ph: {
    label: 'pH de la solución',
    unit: 'pH',
    pin: 34,
    minimum: 0,
    maximum: 14,
    normal: [5.6, 6],
    critical: [4.5, 7.5],
  },
  humidity: {
    label: 'Humedad del aire',
    unit: '% HR',
    pin: 33,
    minimum: 0,
    maximum: 100,
    normal: [50, 70],
    critical: [30, 90],
  },
  ec: {
    label: 'Conductividad',
    unit: 'mS/cm',
    pin: 32,
    minimum: 0,
    maximum: 5,
    normal: [1.2, 1.8],
    critical: [0.5, 3],
  },
  temperature: {
    label: 'Temperatura del aire',
    unit: '°C',
    pin: 35,
    minimum: 0,
    maximum: 45,
    normal: [19, 24],
    critical: [10, 32],
  },
}
const spec = (key: MetricKey) => data.value?.specs[key] || fallback[key]
const metric = (key: MetricKey) => data.value?.latest?.metrics[key]
const format = (v: number, key: MetricKey) =>
  v.toLocaleString('es-AR', {
    minimumFractionDigits: key === 'ph' || key === 'ec' ? 2 : 1,
    maximumFractionDigits: key === 'ph' || key === 'ec' ? 2 : 1,
  })
const time = (at: number) => new Date(at * 1000).toLocaleTimeString('es-AR')
const lastSeen = computed(() =>
  data.value?.latest
    ? `Última lectura ${time(data.value.latest.captured_at)}`
    : 'Aún no hay lecturas',
)
const summaries = computed(() => [
  { label: 'Métricas disponibles', value: connected.value ? '4 / 4' : '0 / 4' },
  {
    label: 'En objetivo',
    value: connected.value ? keys.filter((k) => metric(k)?.level === 'safe').length : '—',
  },
  {
    label: 'Fuera de objetivo',
    value: connected.value ? keys.filter((k) => metric(k)?.level !== 'safe').length : '—',
  },
  { label: 'Lecturas recibidas', value: data.value?.received.toLocaleString('es-AR') || '0' },
])
function badge(key: MetricKey) {
  if (!connected.value) return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
  switch (metric(key)?.level) {
    case 'critical':
      return 'bg-error-50 text-error-700 dark:bg-error-500/15 dark:text-error-400'
    case 'warning':
      return 'bg-warning-50 text-warning-700 dark:bg-warning-500/15 dark:text-warning-400'
    default:
      return 'bg-success-50 text-success-700 dark:bg-success-500/15 dark:text-success-400'
  }
}
function chartY(value: number, key: MetricKey) {
  const s = spec(key)
  return 85 - ((value - s.minimum) / (s.maximum - s.minimum)) * 80
}
function chartSegments(key: MetricKey) {
  const points = (data.value?.history || []).filter((p) => now.value / 1000 - p.at <= 120)
  const segments: string[][] = [[]]
  points.forEach((p, i) => {
    if (i && p.at - points[i - 1].at > 4) segments.push([])
    const x = Math.max(0, Math.min(300, 300 - (now.value / 1000 - p.at) * 2.5))
    segments[segments.length - 1].push(`${x},${chartY(p.values[key], key)}`)
  })
  return segments.map((s) => s.join(' '))
}
</script>
