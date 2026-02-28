<template>
	<div class="inventory-table">
		<table v-if="items && items.length" class="table table--stack">
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
				<tr v-for="item in items" :key="item.id" data-testid="inventory-row">
					<td data-label="Id">{{ item.id }}</td>
					<td data-label="Nombre">{{ item.name || item.nombre || '-' }}</td>
					<td data-label="Categoría">{{ item.category || '-' }}</td>
					<td data-label="Cantidad">{{ item.stock ?? item.quantity ?? item.cantidad ?? 0 }}</td>
					<td data-label="Acciones">
						<button class="btn btn-sm btn-outline-primary me-2" data-testid="inventory-edit" @click="$emit('edit', item)">Editar</button>
						<button class="btn btn-sm btn-outline-danger" data-testid="inventory-delete" @click="$emit('delete', item)">Eliminar</button>
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

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

.inventory-table .table {
	width: 100%;
	border-collapse: collapse;
}
.inventory-table th,
.inventory-table td {
	border: 1px solid $color-gray-200-legacy;
	padding: 8px 12px;
	text-align: left;
}
.inventory-table .empty {
	color: $color-gray-500-legacy;
	padding: 12px 0;
}

@include media-breakpoint-down(md) {
	.inventory-table .table,
	.inventory-table .table thead,
	.inventory-table .table tbody,
	.inventory-table .table tr,
	.inventory-table .table th,
	.inventory-table .table td {
		display: block;
		width: 100%;
	}

	.inventory-table .table thead {
		display: none;
	}

	.inventory-table .table tr {
		padding: 1rem;
		margin-bottom: 0.75rem;
		background: $color-white;
		border-radius: 12px;
		box-shadow: 0 8px 16px rgba($color-dark, 0.12);
	}

	.inventory-table .table td {
		display: flex;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.35rem 0;
		font-size: 1rem;
	}

	.inventory-table .table td::before {
		content: attr(data-label);
		font-weight: 600;
		color: $text-muted;
		text-transform: uppercase;
		letter-spacing: 0.03em;
		font-size: 0.8rem;
	}
}
</style>
