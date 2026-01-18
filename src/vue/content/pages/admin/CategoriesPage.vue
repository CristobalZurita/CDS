<template>
	<div>
		<AdminToolbar title="Categorías" subtitle="Servicios y clasificaciones" />
		<CategoryList />
	</div>
</template>

<script setup>
import CategoryList from '@/vue/components/admin/CategoryList.vue'
import AdminToolbar from '@/vue/components/admin/AdminToolbar.vue'
</script>

<style scoped>
</style>
