<template>
  <div class="relative" ref="dropdownRef">
    <div
      v-if="pushToast"
      class="fixed end-4 top-4 z-99999 w-[min(28rem,calc(100vw-2rem))] overflow-hidden rounded-2xl border-2 border-error-500 bg-white shadow-theme-xl ring-4 ring-error-500/20 animate-fadeIn dark:bg-gray-900"
      role="alert"
    >
      <div class="flex items-center gap-3 bg-error-500 px-5 py-3 text-white">
        <span class="flex h-10 w-10 shrink-0 animate-pulse items-center justify-center rounded-full bg-white text-xl font-black text-error-500">!</span>
        <div class="flex-1">
          <p class="text-base font-bold uppercase tracking-wide">Alerta crítica</p>
          <p class="text-xs font-medium text-white/80">Lectura fuera de rango detectada</p>
        </div>
        <button
          type="button"
          class="text-2xl leading-none text-white/80 hover:text-white"
          aria-label="Cerrar alerta"
          @click="pushToast = null"
        >
          &times;
        </button>
      </div>
      <RouterLink
        :to="{ name: 'SensorDetalle', params: { id: pushToast.deviceId } }"
        class="block p-5 transition hover:bg-error-50 dark:hover:bg-error-500/10"
        @click="pushToast = null"
      >
        <p class="text-lg font-bold text-gray-800 dark:text-white/90">{{ pushToast.deviceName }}</p>
        <p class="mt-1 text-sm text-error-600 dark:text-error-400">{{ pushToast.message }}</p>
        <span class="mt-4 inline-flex items-center text-sm font-semibold text-brand-500 dark:text-brand-400">
          Ver sensor y revisar lectura <span class="ms-2 text-lg rtl:rotate-180">→</span>
        </span>
      </RouterLink>
    </div>

    <button
      class="relative flex items-center justify-center text-gray-500 transition-colors bg-white border border-gray-200 rounded-full hover:text-dark-900 h-11 w-11 hover:bg-gray-100 hover:text-gray-700 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-white"
      @click="toggleDropdown"
    >
      <span
        :class="{ hidden: !notifying, flex: notifying }"
        class="absolute right-0 top-0.5 z-1 h-2 w-2 rounded-full bg-orange-400"
      >
        <span
          class="absolute inline-flex w-full h-full bg-orange-400 rounded-full opacity-75 -z-1 animate-ping"
        ></span>
      </span>
      <svg
        class="fill-current"
        width="20"
        height="20"
        viewBox="0 0 20 20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M10.75 2.29248C10.75 1.87827 10.4143 1.54248 10 1.54248C9.58583 1.54248 9.25004 1.87827 9.25004 2.29248V2.83613C6.08266 3.20733 3.62504 5.9004 3.62504 9.16748V14.4591H3.33337C2.91916 14.4591 2.58337 14.7949 2.58337 15.2091C2.58337 15.6234 2.91916 15.9591 3.33337 15.9591H4.37504H15.625H16.6667C17.0809 15.9591 17.4167 15.6234 17.4167 15.2091C17.4167 14.7949 17.0809 14.4591 16.6667 14.4591H16.375V9.16748C16.375 5.9004 13.9174 3.20733 10.75 2.83613V2.29248ZM14.875 14.4591V9.16748C14.875 6.47509 12.6924 4.29248 10 4.29248C7.30765 4.29248 5.12504 6.47509 5.12504 9.16748V14.4591H14.875ZM8.00004 17.7085C8.00004 18.1228 8.33583 18.4585 8.75004 18.4585H11.25C11.6643 18.4585 12 18.1228 12 17.7085C12 17.2943 11.6643 16.9585 11.25 16.9585H8.75004C8.33583 16.9585 8.00004 17.2943 8.00004 17.7085Z"
          fill=""
        />
      </svg>
    </button>

    <!-- Dropdown Start -->
    <div
      v-if="dropdownOpen"
      class="absolute ltr:-left-15 ltr:md:-left-13 rtl:-right-15 rtl:md:-right-13 mt-4.25 flex h-120 w-87.5 flex-col rounded-2xl border border-gray-200 bg-white p-3 shadow-theme-lg dark:border-gray-800 dark:bg-gray-dark sm:w-90.25 ltr:xl:left-auto ltr:xl:right-0 rtl:xl:right-auto rtl:xl:left-0 z-50 animate-fadeIn"
    >
      <div
        class="flex items-center justify-between pb-3 mb-3 border-b border-gray-100 dark:border-gray-800"
      >
        <h5 class="text-lg font-semibold text-gray-800 dark:text-white/90">Alertas del invernadero</h5>

        <button @click="closeDropdown" class="text-gray-500 dark:text-gray-400">
          <svg
            class="fill-current"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M6.21967 7.28131C5.92678 6.98841 5.92678 6.51354 6.21967 6.22065C6.51256 5.92775 6.98744 5.92775 7.28033 6.22065L11.999 10.9393L16.7176 6.22078C17.0105 5.92789 17.4854 5.92788 17.7782 6.22078C18.0711 6.51367 18.0711 6.98855 17.7782 7.28144L13.0597 12L17.7782 16.7186C18.0711 17.0115 18.0711 17.4863 17.7782 17.7792C17.4854 18.0721 17.0105 18.0721 16.7176 17.7792L11.999 13.0607L7.28033 17.7794C6.98744 18.0722 6.51256 18.0722 6.21967 17.7794C5.92678 17.4865 5.92678 17.0116 6.21967 16.7187L10.9384 12L6.21967 7.28131Z"
              fill=""
            />
          </svg>
        </button>
      </div>

      <button
        type="button"
        class="mb-3 flex w-full items-center justify-center gap-2 rounded-lg bg-error-50 px-3 py-2 text-theme-sm font-medium text-error-600 transition hover:bg-error-100 dark:bg-error-500/15 dark:text-error-400 dark:hover:bg-error-500/25"
        @click.stop="sendCriticalPush"
      >
        <span class="flex h-5 w-5 items-center justify-center rounded-full bg-error-500 text-xs font-bold text-white">!</span>
        Enviar alerta push crítica
      </button>

      <ul class="flex flex-col h-auto overflow-y-auto custom-scrollbar">
        <li v-for="notification in notifications" :key="notification.id" @click="handleItemClick">
          <a
            class="flex gap-3 rounded-lg border-b border-gray-100 p-3 px-4.5 py-3 hover:bg-gray-100 dark:border-gray-800 dark:hover:bg-white/5"
            href="#"
          >
            <span
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xs font-bold"
              :class="notification.severity === 'critical'
                ? 'bg-error-50 text-error-600 dark:bg-error-500/15 dark:text-error-400'
                : 'bg-warning-50 text-warning-600 dark:bg-warning-500/15 dark:text-orange-400'"
            >
              {{ notification.icon }}
            </span>

            <span class="block">
              <span class="mb-1.5 block text-theme-sm text-gray-500 dark:text-gray-400">
                <span class="font-medium text-gray-800 dark:text-white/90">
                  {{ notification.title }}
                </span>
                {{ notification.message }}
              </span>

              <span class="flex items-center gap-2 text-gray-500 text-theme-xs dark:text-gray-400">
                <span>{{ notification.type }}</span>
                <span class="w-1 h-1 bg-gray-400 rounded-full"></span>
                <span>{{ notification.time }}</span>
              </span>
            </span>
          </a>
        </li>
      </ul>

      <router-link
        to="#"
        class="mt-3 flex justify-center rounded-lg border border-gray-300 bg-white p-3 text-theme-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 hover:text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/3 dark:hover:text-gray-200"
        @click="handleViewAllClick"
      >
        Ver todas las alertas
      </router-link>
    </div>
    <!-- Dropdown End -->
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  bateriaBaja,
  dispositivos,
  formatoFechaHora,
  medicionEnAlerta,
  revisionVencida,
  type Dispositivo,
  type Medicion,
} from '@/data/mockSensores'

const dropdownOpen = ref(false)
const notifying = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)
const simulatedNotifications = ref<Notification[]>([])
const pushToast = ref<{ deviceId: string; deviceName: string; message: string } | null>(null)

type Notification = {
  id: string
  title: string
  message: string
  type: string
  time: string
  severity: 'critical' | 'warning'
  icon: string
}

const readingAlert = (device: Dispositivo, measurement: Medicion): Notification => {
  const { valor } = measurement.ultimaLectura
  const { min, max } = measurement.rangoNormal
  const direction = valor < min ? 'por debajo' : 'por encima'

  return {
    id: `reading-${device.id}-${measurement.tipo}`,
    title: `${device.codigo} · ${device.nombre}`,
    message: `Lectura ${direction} del rango (${valor} ${measurement.tipo}; normal ${min}-${max})`,
    type: 'Lectura anómala',
    time: formatoFechaHora(measurement.ultimaLectura.fecha),
    severity: 'critical',
    icon: '!',
  }
}

const sensorNotifications = computed<Notification[]>(() => {
  const alerts: Notification[] = []

  for (const device of dispositivos) {
    for (const measurement of device.mediciones) {
      if (medicionEnAlerta(device, measurement)) alerts.push(readingAlert(device, measurement))
    }

    if (revisionVencida(device)) {
      alerts.push({
        id: `revision-${device.id}`,
        title: `${device.codigo} · ${device.nombre}`,
        message: 'Tiene una revisión de mantenimiento vencida',
        type: 'Mantenimiento',
        time: `Programada para ${device.proximaRevision}`,
        severity: 'warning',
        icon: 'M',
      })
    }

    if (bateriaBaja(device)) {
      alerts.push({
        id: `battery-${device.id}`,
        title: `${device.codigo} · ${device.nombre}`,
        message: `Batería baja (${device.bateria}%)`,
        type: 'Estado del dispositivo',
        time: 'Requiere atención',
        severity: 'warning',
        icon: 'B',
      })
    }
  }

  return alerts.slice(0, 8)
})

const notifications = computed<Notification[]>(() => [
  ...simulatedNotifications.value,
  ...sensorNotifications.value,
].slice(0, 8))

const sendCriticalPush = async () => {
  const device = dispositivos.find((item) =>
    item.mediciones.some((measurement) => medicionEnAlerta(item, measurement)),
  ) ?? dispositivos[0]
  const measurement = device.mediciones.find((item) => medicionEnAlerta(device, item)) ?? device.mediciones[0]
  const alert = readingAlert(device, measurement)
  const simulatedAlert: Notification = {
    ...alert,
    id: `push-${Date.now()}`,
    title: `Alerta push · ${alert.title}`,
    message: `Lectura crítica detectada. ${alert.message}`,
    time: 'Ahora',
  }

  simulatedNotifications.value = [simulatedAlert, ...simulatedNotifications.value]
  notifying.value = true
  pushToast.value = {
    deviceId: device.id,
    deviceName: `${device.codigo} · ${device.nombre}`,
    message: `${measurement.ultimaLectura.valor} ${measurement.tipo}. ${alert.message}`,
  }
  window.setTimeout(() => {
    pushToast.value = null
  }, 6000)

  if (!('Notification' in window)) return

  let permission = Notification.permission
  if (permission === 'default') permission = await Notification.requestPermission()
  if (permission !== 'granted') return

  new Notification('Lectura crítica del invernadero', {
    body: `${device.codigo}: ${measurement.ultimaLectura.valor} ${measurement.tipo}`,
    icon: '/images/logo/logo-icon.svg',
    tag: simulatedAlert.id,
  })
}

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value
  notifying.value = notifications.value.length > 0 && !dropdownOpen.value
}

const closeDropdown = () => {
  dropdownOpen.value = false
}

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    closeDropdown()
  }
}

const handleItemClick = (event: Event) => {
  event.preventDefault()
  console.log('Notification item clicked')
  closeDropdown()
}

const handleViewAllClick = (event: Event) => {
  event.preventDefault()
  console.log('View All Notifications clicked')
  closeDropdown()
}

onMounted(() => {
  notifying.value = notifications.value.length > 0
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
