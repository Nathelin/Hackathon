<template>
  <div class="min-h-screen xl:flex">
    <app-sidebar />
    <Backdrop />
    <div
      class="min-w-0 flex-1 transition-all duration-300 ease-in-out"
      :class="[isExpanded || isHovered ? 'xl:ms-[290px]' : 'xl:ms-[90px]']"
    >
      <app-header />
      <div class="mx-auto max-w-(--breakpoint-2xl) p-4 pb-20 md:p-6 md:pb-6">
        <p
          v-if="route.path !== '/' && route.path !== '/invernadero1'"
          class="mb-4 rounded-xl bg-warning-50 p-3 text-sm text-warning-700 dark:bg-warning-500/10 dark:text-warning-400"
        >
          Vista de demostración con datos de ejemplo. Las lecturas del ESP32 están en
          <router-link to="/" class="font-semibold underline">Invernadero 1</router-link>.
        </p>
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import { useSidebar } from '@/composables/useSidebar'
import { useRoute } from 'vue-router'
import Backdrop from './Backdrop.vue'
const { isExpanded, isHovered } = useSidebar()
const route = useRoute()
</script>
