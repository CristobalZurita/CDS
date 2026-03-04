<template>
  <Footer>
    <FooterBlock :darken="false" :row="true">
      <FooterColumn
        title="Sobre el taller"
        faIcon="pi pi-lightbulb me-2"
        :description="[
          `Cirujano de Sintetizadores es un taller especializado en reparación, restauración y modificación de sintetizadores, teclados y equipos de audio profesionales.`,
          `Trabajamos con diagnóstico detallado, repuestos de calidad y un enfoque orientado a conservar y realzar el carácter sonoro original de cada instrumento.`
        ]"
        :links="[]"
        :display-links-as-buttons="false"
      />

      <FooterColumn
        title="Redes y presencia"
        faIcon=""
        :description="[]"
        :links="[
          { label: `Instagram`, href: `https://www.instagram.com/cirujanodesintetizadores/`, faIcon: `fa-brands fa-instagram` },
          { label: `Facebook`, href: `https://www.facebook.com/Cirujanodesintetizadores/`, faIcon: `fa-brands fa-facebook` }
        ]"
        :display-links-as-buttons="true"
      />

      <FooterColumn
        title="Información de contacto"
        faIcon="pi pi-envelope me-2 pe-1"
        :description="[
          `Valparaíso – Chile`,
          `Atención con coordinación previa.`
        ]"
        :links="[
          { label: `+56 9 8295 7538`, href: `tel:+56982957538`, faIcon: `pi pi-phone` },
          { label: `contacto@cirujanodesintetizadores.com`, href: `mailto:contacto@cirujanodesintetizadores.com`, faIcon: `fa-regular fa-envelope` }
        ]"
        :display-links-as-buttons="false"
      />
    </FooterBlock>

    <FooterBlock :darken="false" :row="false">
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

    <FooterBlock :darken="true" :row="false">
      <FooterCopyright
        holder="Cirujano de Sintetizadores"
        url="https://www.cirujanodesintetizadores.cl"
        license="Todos los derechos reservados"
      />
    </FooterBlock>
  </Footer>
</template>

<script setup>
import Footer from "/src/vue/components/footer/Footer.vue"
import FooterBlock from "/src/vue/components/footer/FooterBlock.vue"
import FooterColumn from "/src/vue/components/footer/FooterColumn.vue"
import FooterCopyright from "/src/vue/components/footer/FooterCopyright.vue"
</script>
