<template>
  <main class="profile-page">
    <section class="profile-header">
      <div class="header-content">
        <div class="avatar">{{ userInitials }}</div>
        <div>
          <h1>{{ user.fullName || 'Cliente' }}</h1>
          <p class="subtitle">Cliente desde {{ memberSince }}</p>
        </div>
      </div>

      <button class="btn-secondary" data-testid="profile-edit-toggle" @click="toggleEditMode">
        {{ editMode ? 'Cancelar' : 'Editar perfil' }}
      </button>
    </section>

    <p v-if="error" class="profile-error">{{ error }}</p>
    <p v-if="success" class="profile-success">{{ success }}</p>

    <section class="profile-grid">
      <article class="card">
        <h2>Informacion personal</h2>

        <div class="field" v-if="!editMode">
          <span>Email</span>
          <p>{{ user.email || '—' }}</p>
        </div>
        <label class="field" v-else>
          <span>Email</span>
          <input v-model.trim="formData.email" type="email" data-testid="profile-email-input" />
        </label>

        <div class="field" v-if="!editMode">
          <span>Nombre completo</span>
          <p>{{ user.fullName || '—' }}</p>
        </div>
        <label class="field" v-else>
          <span>Nombre completo</span>
          <input v-model.trim="formData.fullName" type="text" data-testid="profile-name-input" />
        </label>

        <div class="field" v-if="!editMode">
          <span>Telefono</span>
          <p>{{ user.phone || '—' }}</p>
        </div>
        <label class="field" v-else>
          <span>Telefono</span>
          <input v-model.trim="formData.phone" type="tel" data-testid="profile-phone-input" />
        </label>

        <div class="field" v-if="!editMode">
          <span>Direccion</span>
          <p>{{ user.address || '—' }}</p>
        </div>
        <label class="field" v-else>
          <span>Direccion</span>
          <input v-model.trim="formData.address" type="text" data-testid="profile-address-input" />
        </label>

        <button
          v-if="editMode"
          class="btn-primary"
          data-testid="profile-save"
          :disabled="isLoading"
          @click="saveProfile"
        >
          {{ isLoading ? 'Guardando...' : 'Guardar cambios' }}
        </button>
      </article>

      <article class="card">
        <h2>Preferencias</h2>

        <label class="checkbox-row">
          <input v-model="preferences.emailNotifications" type="checkbox" />
          <span>Notificaciones por email</span>
        </label>

        <label class="checkbox-row">
          <input v-model="preferences.whatsappNotifications" type="checkbox" />
          <span>Notificaciones por WhatsApp</span>
        </label>

        <label class="checkbox-row">
          <input v-model="preferences.smsNotifications" type="checkbox" />
          <span>Notificaciones por SMS</span>
        </label>

        <button class="btn-secondary" data-testid="profile-preferences-save" @click="savePreferences">
          Guardar preferencias
        </button>
      </article>

      <article class="card">
        <h2>Estadisticas</h2>
        <div class="stat-row">
          <span>Reparaciones totales</span>
          <strong>{{ totalRepairs }}</strong>
        </div>
        <div class="stat-row">
          <span>Total invertido</span>
          <strong>{{ totalSpent }}</strong>
        </div>
        <div class="stat-row">
          <span>Promedio reparacion</span>
          <strong>{{ avgRepairDays }} dias</strong>
        </div>
      </article>

      <article class="card">
        <h2>Seguridad</h2>
        <button class="btn-secondary" data-testid="profile-open-password-modal" @click="showChangePassword = true">
          Cambiar contrasena
        </button>
        <button class="btn-danger" data-testid="profile-open-delete-modal" @click="showDeleteAccount = true">
          Eliminar cuenta
        </button>
      </article>
    </section>

    <div v-if="showChangePassword" class="modal-overlay" @click="showChangePassword = false">
      <section class="modal" @click.stop>
        <h3>Cambiar contrasena</h3>
        <label class="field">
          <span>Contrasena actual</span>
          <input v-model="passwordForm.current" :type="showPassword ? 'text' : 'password'" data-testid="profile-password-current" />
        </label>
        <label class="field">
          <span>Nueva contrasena</span>
          <input v-model="passwordForm.next" :type="showPassword ? 'text' : 'password'" data-testid="profile-password-new" />
        </label>
        <label class="field">
          <span>Confirmar contrasena</span>
          <input v-model="passwordForm.confirm" :type="showPassword ? 'text' : 'password'" data-testid="profile-password-confirm" />
        </label>

        <label class="checkbox-row">
          <input v-model="showPassword" type="checkbox" />
          <span>Mostrar contrasena</span>
        </label>

        <div class="modal-actions">
          <button class="btn-secondary" data-testid="profile-password-cancel" @click="showChangePassword = false">
            Cancelar
          </button>
          <button class="btn-primary" data-testid="profile-password-save" @click="changePassword">
            Guardar
          </button>
        </div>
      </section>
    </div>

    <div v-if="showDeleteAccount" class="modal-overlay" @click="showDeleteAccount = false">
      <section class="modal" @click.stop>
        <h3>Eliminar cuenta</h3>
        <p>Esta accion es irreversible.</p>
        <div class="modal-actions">
          <button class="btn-secondary" data-testid="profile-delete-cancel" @click="showDeleteAccount = false">
            Cancelar
          </button>
          <button class="btn-danger" data-testid="profile-delete-confirm" @click="deleteAccount">
            Confirmar eliminacion
          </button>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { useProfilePage } from '@new/composables/useProfilePage'

const {
  editMode,
  isLoading,
  error,
  success,
  user,
  formData,
  preferences,
  showChangePassword,
  showDeleteAccount,
  showPassword,
  passwordForm,
  userInitials,
  memberSince,
  totalRepairs,
  totalSpent,
  avgRepairDays,
  toggleEditMode,
  saveProfile,
  savePreferences,
  changePassword,
  deleteAccount
} = useProfilePage()
</script>

<style scoped>
.profile-page {
  padding: 1rem;
  display: grid;
  gap: 1rem;
}

.profile-header,
.card,
.modal {
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.9rem;
  background: var(--cds-white);
}

.profile-header,
.card,
.modal {
  padding: 0.95rem;
}

.profile-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar {
  width: 52px;
  height: 52px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  border: 1px solid color-mix(in srgb, var(--cds-primary) 40%, white);
  background: color-mix(in srgb, var(--cds-primary) 12%, white);
  font-weight: var(--cds-font-bold);
}

.profile-header h1 {
  margin: 0;
  font-size: var(--cds-text-2xl);
}

.subtitle {
  margin: 0.3rem 0 0;
  color: var(--cds-text-muted);
}

.profile-error,
.profile-success {
  margin: 0;
  border-radius: 0.6rem;
  padding: 0.75rem;
}

.profile-error {
  border: 1px solid #f4c7c3;
  background: #fef3f2;
  color: #b42318;
}

.profile-success {
  border: 1px solid #b7ebc6;
  background: #f0fdf4;
  color: #166534;
}

.profile-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.card {
  display: grid;
  gap: 0.6rem;
}

.card h2 {
  margin: 0;
  font-size: var(--cds-text-xl);
}

.field {
  display: grid;
  gap: 0.3rem;
}

.field span {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.field p {
  margin: 0;
}

.field input {
  min-height: 44px;
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  border-radius: 0.55rem;
  padding: 0.65rem 0.75rem;
  font-size: var(--cds-text-base);
}

.checkbox-row {
  display: flex;
  gap: 0.55rem;
  align-items: center;
}

.btn-primary,
.btn-secondary,
.btn-danger {
  min-height: 44px;
  padding: 0.65rem 0.9rem;
  border-radius: 0.55rem;
  font-size: var(--cds-text-base);
  border: 1px solid transparent;
  cursor: pointer;
}

.btn-primary {
  border-color: var(--cds-primary);
  background: var(--cds-primary);
  color: var(--cds-white);
}

.btn-secondary {
  border-color: color-mix(in srgb, var(--cds-light) 65%, white);
  background: var(--cds-white);
  color: var(--cds-text-normal);
}

.btn-danger {
  border-color: #dc2626;
  background: #dc2626;
  color: #fff;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: grid;
  place-items: center;
  padding: 1rem;
}

.modal {
  width: min(100%, 520px);
  display: grid;
  gap: 0.65rem;
}

.modal h3,
.modal p {
  margin: 0;
}

.modal-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: flex-end;
}

@media (min-width: 900px) {
  .profile-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
