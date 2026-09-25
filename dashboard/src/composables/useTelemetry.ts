import { computed, onMounted, onUnmounted, ref } from 'vue'

export type MetricKey = 'ph' | 'humidity' | 'ec' | 'temperature'
export type Level = 'safe' | 'warning' | 'critical'
export interface Metric {
  pin: number
  raw: number
  value: number
  level: Level
  advice: string
}
export interface Spec {
  label: string
  unit: string
  pin: number
  minimum: number
  maximum: number
  normal: [number, number]
  critical: [number, number]
}
export interface AlertEvent {
  id: string
  label: string
  metric: MetricKey
  value: number
  unit: string
  at: number
  message: string
  resolved: boolean
  email: string
}
export interface Snapshot {
  connected: boolean
  age_seconds: number | null
  received: number
  profile: { name: string; note: string; sources: { title: string; url: string }[] }
  specs: Record<MetricKey, Spec>
  latest: { metrics: Record<MetricKey, Metric>; captured_at: number; received_at: number } | null
  history: { at: number; values: Record<MetricKey, number> }[]
  alerts: AlertEvent[]
  bridge: { status: string; reason: string; port: string }
  email_configured: boolean
  alert_confirmation_seconds: number
}

const data = ref<Snapshot | null>(null)
const error = ref('')
const lastResponse = ref(0)
const now = ref(Date.now())
const permission = ref<NotificationPermission | 'unsupported'>('default')
const seen = new Set<string>()
const criticalToasts = ref<AlertEvent[]>([])
function dismissCritical(id: string) {
  criticalToasts.value = criticalToasts.value.filter((a) => a.id !== id)
}
function previewCritical() {
  const preview: AlertEvent = {
    id: `preview-${Date.now()}`,
    label: 'Prueba de aviso crítico',
    metric: 'ph',
    value: 4,
    unit: 'pH',
    at: Date.now() / 1000,
    resolved: false,
    email: 'disabled',
    message: 'Este es un aviso de prueba. No modifica las lecturas ni envía correos.',
  }
  criticalToasts.value = [preview, ...criticalToasts.value].slice(0, 8)
}
let subscribers = 0
let generation = 0
let timer: ReturnType<typeof setTimeout> | undefined
let ticker: ReturnType<typeof setInterval> | undefined
let request: AbortController | undefined
const connected = computed(
  () => !error.value && !!data.value?.connected && now.value - lastResponse.value < 4000,
)
const connectionText = computed(
  () =>
    error.value ||
    (connected.value
      ? 'ESP32 conectado · datos en vivo'
      : data.value?.bridge.reason || 'Conectando con la API local…'),
)

async function poll(run: number) {
  const controller = new AbortController()
  request = controller
  const timeout = setTimeout(() => controller.abort(), 2500)
  try {
    const response = await fetch('/api/v1/telemetry/latest', {
      cache: 'no-store',
      signal: controller.signal,
    })
    if (!response.ok) throw new Error(`API HTTP ${response.status}`)
    const next = (await response.json()) as Snapshot
    if (!next.specs || !Array.isArray(next.alerts)) throw new Error('API incompatible')
    if (run !== generation) return
    data.value = next
    lastResponse.value = Date.now()
    now.value = Date.now()
    error.value = ''
    for (const alert of next.alerts) {
      if (!seen.has(alert.id) && !alert.resolved && Date.now() - alert.at * 1000 < 15000) {
        criticalToasts.value = [...criticalToasts.value, alert].slice(-8)
        if (permission.value === 'granted') {
          try {
            new Notification(`HydroGuard · ${alert.label}`, {
              body: `${alert.value} ${alert.unit}. ${alert.message}`,
              tag: alert.id,
            })
          } catch {
            /* Un aviso del sistema no debe interrumpir la telemetría. */
          }
        }
      }
      seen.add(alert.id)
    }
    if (seen.size > 300) {
      seen.clear()
      next.alerts.forEach((a) => seen.add(a.id))
    }
  } catch {
    if (run === generation) error.value = 'API sin respuesta. Reintentando automáticamente…'
  } finally {
    clearTimeout(timeout)
    if (run === generation && subscribers > 0) timer = setTimeout(() => void poll(run), 500)
  }
}

export function useTelemetry() {
  onMounted(() => {
    permission.value = 'Notification' in window ? Notification.permission : 'unsupported'
    subscribers += 1
    if (subscribers === 1) {
      generation += 1
      ticker = setInterval(() => {
        now.value = Date.now()
      }, 500)
      void poll(generation)
    }
  })
  onUnmounted(() => {
    subscribers -= 1
    if (!subscribers) {
      generation += 1
      clearTimeout(timer)
      clearInterval(ticker)
      request?.abort()
    }
  })
  async function enableNotifications() {
    if ('Notification' in window) permission.value = await Notification.requestPermission()
  }
  return {
    data,
    connected,
    connectionText,
    permission,
    enableNotifications,
    now,
    criticalToasts,
    dismissCritical,
    previewCritical,
  }
}
