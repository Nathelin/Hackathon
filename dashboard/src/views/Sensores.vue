<template>
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6">

        <div class="col-span-12 xl:col-span-7">
            <RecentOrders />
        </div>
    </div>
  </AdminLayout>
</template>


<script setup lang="ts">
import AdminLayout from '../components/layout/AdminLayout.vue'
import RecentOrders from '../components/ecommerce/RecentOrders.vue'
</script>