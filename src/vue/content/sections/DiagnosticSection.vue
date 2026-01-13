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
            <DiagnosticWizard />
        </div>

    </section>
</template>

<script setup>
// Solo importamos el Wizard, PageWrapper ya lo maneja en Master.vue
import DiagnosticWizard from "@/vue/components/articles/DiagnosticWizard.vue";
</script>

<style lang="scss" scoped>
// Importamos variables gracias al arreglo en vite.config.js
@import '@/scss/variables';

.diagnostic-section {
    background-color: $light; // Vintage Beige
    padding-top: 4rem;
    padding-bottom: 4rem;
    position: relative;
}

.section-title {
    font-family: $headings-font-family; // Oswald
    color: $primary;     // Naranja
    font-size: 3rem;
    text-align: center;
    margin-bottom: 1rem;
    text-transform: uppercase;
}

.section-subtitle {
    text-align: center;
    font-size: 1.2rem;
    color: $dark;   // Vintage Black
    margin-bottom: 3rem;
    font-family: $font-family-base;
}

.wizard-container {
    // Esto permite que el wizard respire
    max-width: 900px; 
}
</style>
