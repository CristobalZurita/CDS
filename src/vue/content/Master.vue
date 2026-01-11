<template>
    <!-- Navigation -->
    <Navigation logo="images/logo/logo_square_002.png"
                label="*Cirujano* de Sintetizadores"/>

        <!-- Content Display -->
        <main class="site-body">
            <router-view/>
        </main>

    <!-- Floating Quote Button - Visible in all pages -->
    <FloatingQuoteButton/>

    <!-- Toast Notifications -->
    <ToastNotification ref="toastComponent" />

    <!-- Footer -->
    <Footer>
        <FooterBlock :darken="false"
                     :row="true">
            <FooterColumn title="Sobre el taller"
                          faIcon="pi pi-lightbulb me-2"
                          :description="[
                              `Cirujano de Sintetizadores es un taller especializado en reparación, restauración y modificación de sintetizadores, teclados y equipos de audio profesionales.`,
                              `Trabajamos con diagnóstico detallado, repuestos de calidad y un enfoque orientado a conservar y realzar el carácter sonoro original de cada instrumento.`
                          ]"
                          :links="[
                              {label: `Política de privacidad`, href: `/privacy-policy`, faIcon: null},
                              {label: `Términos y condiciones`, href: `/license`, faIcon: null},
                              {label: `Repositorio del proyecto`, href: `https://github.com/CristobalZurita/cirujano-front`, faIcon: null},
                          ]"
                          :displayLinksAsButtons="false"/>

            <FooterColumn title="Redes y presencia"
                          faIcon=""
                          :description="[
                          ]"
                          :links="[
                              {label: `Instagram`, href: `https://www.instagram.com/cirujanodesintetizadores/`, faIcon: `fa-brands fa-instagram`},
                              {label: `Facebook`, href: `https://www.facebook.com/Cirujanodesintetizadores/`, faIcon: `fa-brands fa-facebook`},
                          ]"
                          :displayLinksAsButtons="true"/>

            <FooterColumn title="Información de contacto"
                          faIcon="pi pi-envelope me-2 pe-1"
                          :description="[
                              `Valparaíso – Chile`,
                              `Atención con coordinación previa.`
                          ]"
                          :links="[
                              {label: `+56 9 8295 7538`, href: `tel:+56982957538`, faIcon: 'pi pi-phone'},
                              {label: `contacto@cirujanodesintetizadores.com`, href: `mailto:contacto@cirujanodesintetizadores.com`, faIcon: 'fa-regular fa-envelope'},
                          ]"
                          :displayLinksAsButtons="false"/>
        </FooterBlock>

        <FooterBlock :darken="true"
                     :row="false">
            <FooterCopyright holder="Cirujano de Sintetizadores"
                             url="https://www.cirujanodesintetizadores.cl"
                             license="Todos los derechos reservados"/>
        </FooterBlock>
    </Footer>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navigation from "/src/vue/components/nav/Navigation.vue"
import Footer from "/src/vue/components/footer/Footer.vue"
import FooterBlock from "/src/vue/components/footer/FooterBlock.vue"
import FooterCopyright from "/src/vue/components/footer/FooterCopyright.vue"
import FooterColumn from "/src/vue/components/footer/FooterColumn.vue"
import FloatingQuoteButton from "/src/vue/components/widgets/FloatingQuoteButton.vue"
import ToastNotification from "/src/vue/components/system/ToastNotification.vue"
import { setToastComponent } from '/src/services/toastService.js'

const toastComponent = ref(null)

onMounted(() => {
  // Initialize toast service with component reference
  if (toastComponent.value) {
    setToastComponent(toastComponent.value)
  }
})
</script>

<style lang="scss">
@import "/src/scss/_theming.scss";

.site-body {
  padding-top: var(--navbar-height, 120px);
}
</style>
