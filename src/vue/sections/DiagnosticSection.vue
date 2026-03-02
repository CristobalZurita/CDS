<template>
    <!-- ID 'diagnostico' para el scroll del botón flotante -->
    <section id="diagnostico" class="diagnostic-section">
        
        <!-- Header de la sección -->
        <div class="container">
            <h2 class="section-title">Sistema de Cotización Online</h2>
            <p class="section-subtitle">Diagnóstico asistido para sintetizadores analógicos y digitales.</p>
        </div>

        <!-- El Componente Wizard Principal -->
        <div class="container wizard-container">
            <InteractiveInstrumentDiagnostic />
        </div>

    </section>
</template>

<script setup>
// Solo importamos el Wizard, PageWrapper ya lo maneja en Master.vue
import InteractiveInstrumentDiagnostic from "@/vue/components/quotation/InteractiveInstrumentDiagnostic.vue";
</script>
