<template>
  <div class="flex flex-wrap items-center gap-1.5">
    <span :class="claseBase + ' ' + clasesEstado[estado]">{{ estadoSensor[estado].label }}</span>
    <span v-if="alerta" :class="claseBase + ' ' + claseAlerta">Fuera de rango</span>
  </div>
</template>

<script setup lang="ts">
import { estadoSensor, type SensorEstado } from '@/data/mockSensores'

defineProps<{
  estado: SensorEstado
  alerta?: boolean
}>()

const claseBase = 'inline-flex items-center rounded-full px-2 py-0.5 text-theme-xs font-medium'

const clasesEstado: Record<SensorEstado, string> = {
  operativo: 'bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-500',
  revision: 'bg-warning-50 text-warning-600 dark:bg-warning-500/15 dark:text-orange-400',
  sin_conexion:
    'bg-blue-light-50 text-blue-light-500 dark:bg-blue-light-500/15 dark:text-blue-light-500',
  fuera_servicio: 'bg-error-50 text-error-600 dark:bg-error-500/15 dark:text-error-500',
}

const claseAlerta = 'bg-error-50 text-error-600 dark:bg-error-500/15 dark:text-error-500'
</script>
