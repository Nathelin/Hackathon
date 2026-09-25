<template>
  <div ref="root" class="relative">
    <button
      type="button"
      aria-label="Ver alertas del ESP32"
      :aria-expanded="open"
      class="relative flex h-11 w-11 items-center justify-center rounded-full border border-gray-200 bg-white text-gray-600 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-300"
      @click="open = !open"
    >
      <BellIcon class="h-5 w-5" />
      <span
        v-if="alerts.some((a) => !a.resolved)"
        class="absolute end-0 top-0 h-2.5 w-2.5 rounded-full bg-error-500"
      />
    </button>
    <div
      v-if="open"
      class="absolute end-0 z-50 mt-3 w-[min(20rem,calc(100vw-2rem))] rounded-2xl border border-gray-200 bg-white p-4 shadow-theme-lg dark:border-gray-800 dark:bg-gray-900"
    >
      <h2 class="font-semibold text-gray-800 dark:text-white/90">Alertas · Invernadero 1</h2>
      <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">{{ connectionText }}</p>
      <button
        type="button"
        class="mt-3 rounded-lg border border-error-200 px-3 py-2 text-sm font-medium text-error-600 dark:text-error-400"
        @click="testAlert"
      >
        Probar aviso crítico
      </button>
      <p v-if="!alerts.length" class="mt-4 text-sm text-gray-500 dark:text-gray-400">
        Sin alertas confirmadas en esta sesión.
      </p>
      <ul class="mt-3 max-h-72 space-y-3 overflow-y-auto">
        <li
          v-for="alert in alerts.slice(0, 8)"
          :key="alert.id"
          class="rounded-lg bg-error-50 p-3 text-sm text-gray-800 dark:bg-error-500/10 dark:text-gray-200"
        >
          <p class="font-semibold">{{ alert.label }} · {{ alert.value }} {{ alert.unit }}</p>
          <p class="mt-1">{{ alert.message }}</p>
          <p class="mt-1 text-xs">{{ alert.resolved ? 'Recuperado' : 'Aviso registrado' }}</p>
        </li>
      </ul>
      <RouterLink
        to="/"
        class="mt-4 block text-sm font-semibold text-brand-600 dark:text-brand-400"
        @click="open = false"
        >Ver lecturas y configurar avisos</RouterLink
      >
    </div>
  </div>
  <Teleport to="body">
    <section
      v-if="criticalToasts.length"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
      class="fixed end-4 top-20 z-[100000] w-[min(26rem,calc(100vw-2rem))] rounded-2xl border border-error-300 bg-white p-5 shadow-theme-lg dark:border-error-500/50 dark:bg-gray-900"
      data-testid="critical-toast"
    >
      <div class="flex items-start justify-between gap-3">
        <h2 class="font-semibold text-error-600 dark:text-error-400">
          {{
            criticalToasts[0]!.id.startsWith('preview-')
              ? 'Prueba de alerta'
              : '¡Evento crítico detectado!'
          }}
        </h2>
        <button
          type="button"
          aria-label="Cerrar aviso crítico"
          class="shrink-0 rounded-lg px-2 py-1 text-gray-600 dark:text-gray-300"
          @click="dismissCritical(criticalToasts[0]!.id)"
        >
          ✕
        </button>
      </div>
      <p class="mt-2 font-semibold text-gray-800 dark:text-gray-100">
        {{ criticalToasts[0]!.label }} · {{ criticalToasts[0]!.value }}
        {{ criticalToasts[0]!.unit }}
      </p>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">{{ criticalToasts[0]!.message }}</p>
      <p class="mt-3 text-xs text-gray-500 dark:text-gray-400">
        Invernadero 1 · Tanque 1 · Valor simulado al registrar el evento
      </p>
      <p v-if="criticalToasts.length > 1" class="mt-2 text-xs text-error-600 dark:text-error-400">
        Otros {{ criticalToasts.length - 1 }} avisos pendientes
      </p>
    </section>
  </Teleport>
</template>
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import BellIcon from '@/icons/BellIcon.vue'
import { useTelemetry } from '@/composables/useTelemetry'
const { data, connectionText, criticalToasts, dismissCritical, previewCritical } = useTelemetry()
const alerts = computed(() => data.value?.alerts || [])
const open = ref(false)
function testAlert() {
  previewCritical()
  open.value = false
}
const root = ref<HTMLElement | null>(null)
function outside(event: MouseEvent) {
  if (!root.value?.contains(event.target as Node)) open.value = false
}
onMounted(() => document.addEventListener('click', outside))
onUnmounted(() => document.removeEventListener('click', outside))
</script>
