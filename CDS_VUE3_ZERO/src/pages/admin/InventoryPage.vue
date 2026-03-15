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
                  <button class="btn-secondary" :disabled="loading" @click="startEdit(item)">Editar</button>
                  <button class="btn-danger" :disabled="loading" @click="removeItem(item)">Eliminar</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
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
  filters,
  showForm,
  hasEditing,
  form,
  totalStock,
  lowStockCount,
  formatCurrency,
  loadInventory,
  toggleForm,
  startCreate,
  startEdit,
  saveItem,
  removeItem
} = useInventoryPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped>
.summary-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); padding: .75rem; display: grid; gap: .2rem; }
.summary-card span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.summary-card strong { font-size: var(--cds-text-2xl); }
.summary-grid { display: grid; gap: .7rem; grid-template-columns: repeat(1,minmax(0,1fr)); }
.filters-panel { grid-template-columns: repeat(1,minmax(0,1fr)); }
.filters-panel label { display: grid; gap: .3rem; }
.filters-panel span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.filters-panel input, .filters-panel select { min-height: 44px; border-radius: .55rem; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); padding: .65rem .75rem; font-size: var(--cds-text-base); }
.checkbox-row { display: flex !important; align-items: center; gap: .5rem !important; }
.flag-list { display: flex; flex-wrap: wrap; gap: .35rem; }
.flag-list span { border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); border-radius: 999px; padding: .2rem .55rem; font-size: var(--cds-text-sm); }
.flag-warn { border-color: #ca8a04 !important; background: #fef9c3; }
.flag-ok { border-color: #16a34a !important; background: #dcfce7; }
@media (min-width: 860px) { .summary-grid { grid-template-columns: repeat(3,minmax(0,1fr)); } .filters-panel { grid-template-columns: repeat(2,minmax(0,1fr)); } .form-grid { grid-template-columns: repeat(2,minmax(0,1fr)); } }
</style>
