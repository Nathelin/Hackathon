<template>
  <AdminLayout>
    <h1 class="font-medium text-4xl pb-5">¡Bienvenido!</h1>
    <h2 class="font-medium text-2xl pb-5">Resumen de lecturas recientes del Invernadero 2.</h2>
    <div class="grid grid-cols-12 gap-4 md:gap-6">

      <div class="col-span-12">
        <StatisticsChart />
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import AdminLayout from '../components/layout/AdminLayout.vue'
import StatisticsChart from '../components/ecommerce/StatisticsChart.vue'
</script>
