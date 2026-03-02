<template>
  <AdminLayout title="Magos" subtitle="Asistentes guiados para tareas críticas">
    <div class="wizard-grid">
      <div class="wizard-card">
        <h3>Cliente + Instrumento + OT</h3>
        <p>Ingreso completo guiado para nuevas órdenes.</p>
        <WizardClientIntake @completed="onCompleted" />
      </div>

      <div class="wizard-card">
        <h3>Inventario</h3>
        <p>Ingreso de insumos con SKU y categorías.</p>
        <WizardInventoryItem @completed="onCompleted" />
      </div>

      <div class="wizard-card">
        <h3>Materiales usados</h3>
        <p>Registrar componentes consumidos por OT.</p>
        <WizardMaterialsUsage />
      </div>

      <div class="wizard-card">
        <h3>Tickets</h3>
        <p>Crear consultas internas vinculadas a cliente/OT.</p>
        <WizardTicket @completed="onCompleted" />
      </div>

      <div class="wizard-card">
        <h3>Compras sugeridas</h3>
        <p>Crear carrito interno para compras del cliente.</p>
        <WizardPurchaseRequest @completed="onCompleted" />
      </div>

      <div class="wizard-card">
        <h3>Manual + esquema</h3>
        <p>Subir manuales y asociarlos a un modelo.</p>
        <WizardManualUpload @completed="onCompleted" />
      </div>

      <div class="wizard-card">
        <h3>Firma OT</h3>
        <p>Generar firma de ingreso/retiro para una OT.</p>
        <WizardSignatureRequest @completed="onCompleted" />
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'
import WizardClientIntake from '@/vue/components/admin/wizard/WizardClientIntake.vue'
import WizardInventoryItem from '@/vue/components/admin/wizard/WizardInventoryItem.vue'
import WizardMaterialsUsage from '@/vue/components/admin/wizard/WizardMaterialsUsage.vue'
import WizardTicket from '@/vue/components/admin/wizard/WizardTicket.vue'
import WizardPurchaseRequest from '@/vue/components/admin/wizard/WizardPurchaseRequest.vue'
import WizardManualUpload from '@/vue/components/admin/wizard/WizardManualUpload.vue'
import WizardSignatureRequest from '@/vue/components/admin/wizard/WizardSignatureRequest.vue'

const onCompleted = () => {
  // Placeholder for future toast/feedback
}
</script>
