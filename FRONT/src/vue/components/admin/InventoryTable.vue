<template>
	<div class="inventory-table">
		<table v-if="items && items.length" class="table">
			<thead>
				<tr>
					<th>Id</th>
					<th>Nombre</th>
					<th>Categoría</th>
					<th>Cantidad</th>
					<th>Acciones</th>
				</tr>
			</thead>
			<tbody>
				<tr v-for="item in items" :key="item.id">
					<td>{{ item.id }}</td>
					<td>{{ item.name || item.nombre || '-' }}</td>
					<td>{{ item.category || '-' }}</td>
					<td>{{ item.quantity ?? item.cantidad ?? 0 }}</td>
					<td>
						<button class="btn btn-sm btn-outline-primary me-2" @click="$emit('edit', item)">Editar</button>
						<button class="btn btn-sm btn-outline-danger" @click="$emit('delete', item)">Eliminar</button>
					</td>
				</tr>
			</tbody>
		</table>

		<div v-else class="empty">No hay registros de inventario</div>
	</div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
	items: {
		type: Array,
		default: () => []
	}
})
</script>

<style scoped>
.inventory-table .table {
	width: 100%;
	border-collapse: collapse;
}
.inventory-table th,
.inventory-table td {
	border: 1px solid #e5e7eb;
	padding: 8px 12px;
	text-align: left;
}
.inventory-table .empty {
	color: #6b7280;
	padding: 12px 0;
}
</style>
