<template>
    <!-- Navigation -->
    <Navigation :logo="brandLogo"
                label="*Cirujano* de Sintetizadores"/>

        <!-- Content Display -->
        <main class="site-body">
            <router-view/>
        </main>

    <FloatingWhatsAppButton />
    <FloatingQuoteButton />

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
                          :links="[]"
                          :displayLinksAsButtons="false"/>

            <FooterColumn title="Redes y presencia"
                          faIcon=""
                          :description="[
                          ]"
                          :links="[
                              {label: `Instagram`, href: `https://www.instagram.com/cirujanodesintetizadores/`, faIcon: `fa-brands fa-instagram`},
                              {label: `Facebook`, href: `https://www.facebook.com/Cirujanodesintetizadores/`, faIcon: `fa-brands fa-facebook`},
                              {label: `WhatsApp`, href: `https://wa.me/56982957538`, faIcon: `fa-brands fa-whatsapp`},
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

        <FooterBlock :darken="false"
                     :row="false">
            <div class="footer-legal-row">
                <router-link to="/privacidad">Política de privacidad</router-link>
                <span class="footer-legal-sep">·</span>
                <router-link to="/terminos">Términos y condiciones</router-link>
                <span class="footer-legal-sep">·</span>
                <a href="https://github.com/CristobalZurita/cirujano-front" target="_blank" rel="noopener noreferrer">
                  Repositorio del proyecto
                </a>
            </div>
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
import { ref, provide } from 'vue'
import Navigation from "/src/vue/components/nav/Navigation.vue"
import Footer from "/src/vue/components/footer/Footer.vue"
import FooterBlock from "/src/vue/components/footer/FooterBlock.vue"
import FooterCopyright from "/src/vue/components/footer/FooterCopyright.vue"
import FooterColumn from "/src/vue/components/footer/FooterColumn.vue"
import FloatingQuoteButton from "/src/vue/components/widgets/FloatingQuoteButton.vue"
import FloatingWhatsAppButton from "/src/vue/components/widgets/FloatingWhatsAppButton.vue"
const brandLogo = `${import.meta.env.BASE_URL}images/logo/logo_square_002.webp`

// Provide global injections for child components
const currentPageSections = ref([])
const loaderAnimationStatus = ref('IDLE')
const LoaderAnimationStatus = { IDLE: 'IDLE', LOADING: 'LOADING', LEAVING: 'LEAVING' }

provide('currentPageSections', currentPageSections)
provide('loaderAnimationStatus', loaderAnimationStatus)
provide('LoaderAnimationStatus', LoaderAnimationStatus)
</script>

<style lang="scss">
@use "@/scss/_theming.scss" as *;

.site-body {
  padding-top: var(--navbar-height, 120px);
}

.footer-legal-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
  text-align: center;
  font-size: 1.05rem;
}

.footer-legal-row a {
  color: $color-gray-240-legacy;
  text-decoration: none;
  font-weight: $fw-semibold;
  white-space: nowrap;
}

.footer-legal-row a:hover {
  color: lighten($primary, 15%);
}

.footer-legal-sep {
  color: $color-gray-240-legacy;
}
</style>
