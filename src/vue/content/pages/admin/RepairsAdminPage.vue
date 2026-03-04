<template>
  <AdminLayout title="Reparaciones" subtitle="Flujo y estados del taller">
    <section class="repairs-page">
      <header class="repairs-page__header">
        <h1 class="repairs-page__title">Reparaciones</h1>

        <div class="repairs-page__actions">
          <button
            type="button"
            class="repairs-page__button"
            data-testid="repairs-new"
            @click="showForm = !showForm"
          >
            {{ showForm ? 'Cancelar' : 'Nueva Reparación' }}
          </button>
        </div>
      </header>

      <section v-if="showForm" class="repairs-page__panel">
        <h2 class="repairs-page__panel-title">Crear reparación</h2>
        <RepairForm @saved="onSaved" />
      </section>

      <RepairsList :key="refreshKey" />
    </section>
  </AdminLayout>
</template>

<script setup>
import { ref } from 'vue'
import RepairsList from '@/vue/components/admin/RepairsList.vue'
import RepairForm from '@/vue/components/admin/RepairForm.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const showForm = ref(false)
const refreshKey = ref(0)

function onSaved() {
	showForm.value = false
	refreshKey.value += 1
}
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.repairs-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.repairs-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacer-md);
  flex-wrap: wrap;
}

.repairs-page__title,
.repairs-page__panel-title {
  margin: 0;
  color: var(--color-dark);
  font-weight: 700;
}

.repairs-page__title {
  font-size: var(--text-xl);
}

.repairs-page__panel-title {
  font-size: var(--text-lg);
  margin-bottom: var(--spacer-md);
}

.repairs-page__actions {
  display: flex;
  gap: var(--spacer-sm);
  flex-wrap: wrap;
}

.repairs-page__panel {
  padding: var(--spacer-md);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.repairs-page__button {
  min-height: 40px;
  padding: 0.65rem 0.95rem;
  border: 0;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: var(--color-white);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
}

.repairs-page__button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

@include media-breakpoint-down(md) {
  .repairs-page__header,
  .repairs-page__actions {
    flex-direction: column;
    align-items: stretch;
  }

  .repairs-page__button {
    width: 100%;
  }
}
</style>
