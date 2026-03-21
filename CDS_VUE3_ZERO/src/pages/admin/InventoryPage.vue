<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Inventario</h1>
        <p>Gestión de productos, stock y visibilidad en tienda.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="loading" @click="loadInventory">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
        <button class="btn-primary" :disabled="loading" @click="showForm ? toggleForm() : startCreate()">
          {{ showForm ? 'Cancelar' : 'Nuevo producto' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section class="summary-grid">
      <article class="summary-card">
        <span>Total productos</span>
        <strong>{{ items.length }}</strong>
      </article>
      <article class="summary-card">
        <span>Stock total</span>
        <strong>{{ totalStock }}</strong>
      </article>
      <article class="summary-card">
        <span>Stock bajo</span>
        <strong>{{ lowStockCount }}</strong>
      </article>
    </section>

    <section class="panel-card filters-panel">
      <label>
        <span>Buscar</span>
        <input v-model.trim="filters.search" type="text" placeholder="SKU, nombre o descripción" />
      </label>
      <label>
        <span>Categoría</span>
        <select v-model="filters.category_id">
          <option value="">Todas</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
        </select>
      </label>
      <label class="checkbox-row">
        <input v-model="filters.low_stock_only" type="checkbox" />
        <span>Solo stock bajo</span>
      </label>
      <button class="btn-secondary" :disabled="loading" @click="loadInventory">Aplicar filtros</button>
    </section>

    <section v-if="showForm" class="panel-card">
      <h2>{{ hasEditing ? 'Editar producto' : 'Crear producto' }}</h2>
      <div class="form-grid">
        <label><span>Nombre</span><input v-model.trim="form.name" type="text" /></label>
        <label><span>SKU</span><input v-model.trim="form.sku" type="text" /></label>
        <label>
          <span>Categoría</span>
          <select v-model="form.category_id">
            <option value="">Seleccionar</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
          </select>
        </label>
        <label><span>Precio</span><input v-model.number="form.price" type="number" min="0" /></label>
        <label><span>Stock</span><input v-model.number="form.stock" type="number" min="0" /></label>
        <label><span>Stock mínimo</span><input v-model.number="form.min_quantity" type="number" min="0" /></label>
        <label><span>Familia</span><input v-model.trim="form.family" type="text" /></label>
        <label><span>Origen</span><input v-model.trim="form.origin_status" type="text" /></label>
        <label class="checkbox-row"><input v-model="form.store_visible" type="checkbox" /><span>Visible en tienda</span></label>
        <label class="checkbox-row"><input v-model="form.enabled" type="checkbox" /><span>Habilitado</span></label>
      </div>
      <div class="panel-actions">
        <button class="btn-primary" :disabled="loading" @click="saveItem">
          {{ loading ? 'Guardando...' : (hasEditing ? 'Guardar cambios' : 'Crear producto') }}
        </button>
      </div>
    </section>

    <section class="panel-card">
      <h2>Listado</h2>
      <div v-if="items.length === 0" class="empty-state">No hay productos para los filtros actuales.</div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th><th>SKU</th><th>Nombre</th><th>Categoría</th><th>Stock</th><th>Mínimo</th><th>Precio</th><th>Flags</th><th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.sku }}</td>
              <td>{{ item.name }}</td>
              <td>{{ item.category || '—' }}</td>
              <td>{{ item.stock }}</td>
              <td>{{ item.min_stock }}</td>
              <td>{{ formatCurrency(item.price) }}</td>
              <td>
                <div class="flag-list">
                  <span :class="item.is_low_stock ? 'flag-warn' : 'flag-ok'">{{ item.is_low_stock ? 'LOW' : 'OK' }}</span>
                  <span>{{ item.enabled ? 'ON' : 'OFF' }}</span>
                  <span>{{ item.store_visible ? 'STORE' : 'INTERNAL' }}</span>
                </div>
              </td>
              <td>
                <div class="row-actions">
                  <button class="btn-secondary" :disabled="loading || detailLoading" @click="openItemDetail(item)">Detalle</button>
                  <button class="btn-secondary" :disabled="loading" @click="startEdit(item)">Editar</button>
                  <button class="btn-danger" :disabled="loading" @click="removeItem(item)">Eliminar</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-if="selectedItem || detailLoading || detailError" class="panel-card">
      <div class="panel-head">
        <h2>Detalle de stock</h2>
      </div>

      <p v-if="detailError" class="admin-error">{{ detailError }}</p>
      <p v-else-if="detailLoading" class="empty-state">Cargando detalle del producto...</p>
      <template v-else-if="selectedItem">
        <div class="detail-grid inventory-detail-grid">
          <p><strong>Producto:</strong> {{ selectedItem.name }}</p>
          <p><strong>SKU:</strong> {{ selectedItem.sku }}</p>
          <p><strong>Categoria:</strong> {{ selectedItem.category || '—' }}</p>
          <p><strong>Familia:</strong> {{ selectedItem.family || '—' }}</p>
          <p><strong>Origen:</strong> {{ selectedItem.origin_status || '—' }}</p>
          <p><strong>Ubicacion:</strong> {{ selectedItem.location || '—' }}</p>
          <p><strong>Proveedor:</strong> {{ selectedItem.supplier || '—' }}</p>
          <p><strong>Costo unitario:</strong> {{ formatCurrency(selectedItem.unit_cost) }}</p>
        </div>

        <div class="summary-grid inventory-breakdown-grid">
          <article class="summary-card">
            <span>Fisico</span>
            <strong>{{ selectedItem.stock }}</strong>
          </article>
          <article class="summary-card">
            <span>Disponible</span>
            <strong>{{ selectedItem.available_stock }}</strong>
          </article>
          <article class="summary-card">
            <span>Vendible</span>
            <strong>{{ selectedItem.sellable_stock }}</strong>
          </article>
          <article class="summary-card">
            <span>Reservado</span>
            <strong>{{ selectedItem.quantity_reserved }}</strong>
          </article>
          <article class="summary-card">
            <span>En transito</span>
            <strong>{{ selectedItem.quantity_in_transit }}</strong>
          </article>
          <article class="summary-card">
            <span>Dañado</span>
            <strong>{{ selectedItem.quantity_damaged }}</strong>
          </article>
          <article class="summary-card">
            <span>En trabajo</span>
            <strong>{{ selectedItem.quantity_in_work }}</strong>
          </article>
          <article class="summary-card">
            <span>En revision</span>
            <strong>{{ selectedItem.quantity_under_review }}</strong>
          </article>
          <article class="summary-card">
            <span>Uso interno</span>
            <strong>{{ selectedItem.quantity_internal_use }}</strong>
          </article>
        </div>

        <h3>Movimientos recientes</h3>
        <div v-if="stockMovements.length === 0" class="empty-state">Sin movimientos registrados para este producto.</div>
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Fecha</th><th>Tipo</th><th>Cantidad</th><th>OT</th><th>Notas</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="movement in stockMovements" :key="movement.id">
                <td>{{ movement.id }}</td>
                <td>{{ movement.created_at ? formatDate(movement.created_at) : '—' }}</td>
                <td>{{ movement.movement_type || '—' }}</td>
                <td>{{ movement.quantity }}</td>
                <td>{{ movement.repair_id || '—' }}</td>
                <td>{{ movement.notes || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </section>
  </main>
</template>

<script setup>
import { useInventoryPage } from '@/composables/useInventoryPage'

const {
  items,
  categories,
  loading,
  error,
  detailLoading,
  detailError,
  selectedItem,
  stockMovements,
  filters,
  showForm,
  hasEditing,
  form,
  totalStock,
  lowStockCount,
  formatDate,
  formatCurrency,
  loadInventory,
  openItemDetail,
  toggleForm,
  startCreate,
  startEdit,
  saveItem,
  removeItem
} = useInventoryPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped src="./inventoryPageShared.css"></style>
