<template>
	<div class="inventory-table">
		<table v-if="items && items.length" class="table table--stack">
			<thead>
				<tr>
					<th>Id</th>
					<th>Nombre</th>
					<th>Categoría</th>
					<th>Cantidad</th>
					<th>Disponible</th>
					<th>Taller / OT</th>
					<th>Tienda</th>
					<th>Acciones</th>
				</tr>
			</thead>
			<tbody>
				<tr v-for="item in items" :key="item.id" data-testid="inventory-row">
					<td data-label="Id">{{ item.id }}</td>
					<td data-label="Nombre">{{ item.name || item.nombre || '-' }}</td>
					<td data-label="Categoría">{{ item.category || '-' }}</td>
					<td data-label="Cantidad">{{ item.stock ?? item.quantity ?? item.cantidad ?? 0 }}</td>
					<td data-label="Disponible">{{ item.available_stock ?? item.stock ?? 0 }}</td>
					<td data-label="Taller / OT">
						<div class="d-flex flex-wrap gap-1">
							<span v-if="Number(item.quantity_reserved || 0) > 0" class="badge bg-warning-subtle text-warning-emphasis">
								Reservado {{ item.quantity_reserved }}
							</span>
							<span v-if="Number(item.quantity_in_work || 0) > 0" class="badge bg-info-subtle text-info-emphasis">
								En trabajo {{ item.quantity_in_work }}
							</span>
							<span v-if="Number(item.quantity_internal_use || 0) > 0" class="badge bg-secondary-subtle text-secondary-emphasis">
								Interno {{ item.quantity_internal_use }}
							</span>
							<span
								v-if="Number(item.quantity_reserved || 0) <= 0 && Number(item.quantity_in_work || 0) <= 0 && Number(item.quantity_internal_use || 0) <= 0"
								class="badge bg-light text-body-secondary"
							>
								Sin uso
							</span>
						</div>
					</td>
					<td data-label="Tienda">
						<span v-if="item.store_visible" class="badge bg-success-subtle text-success-emphasis">
							Sí · {{ item.sellable_stock ?? 0 }} vendible
						</span>
						<span v-else class="badge bg-secondary-subtle text-secondary-emphasis">
							No
						</span>
					</td>
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
const _props = defineProps({
	items: {
		type: Array,
		default: () => []
	}
})
</script>
