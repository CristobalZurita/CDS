<template>
  <section class="content-section">
    <div class="section-header">
      <h2>Últimas Reparaciones</h2>
      <router-link to="/admin/repairs" class="btn-link">Ver todas →</router-link>
    </div>
    <RepairsList />
  </section>
</template>

<script setup>
import RepairsList from '@/components/admin/RepairsList.vue'
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/adminDashboardShared.css"></style>
