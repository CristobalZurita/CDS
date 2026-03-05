<template>
    <!-- Sección de Contacto -->
    <PageSection variant="dark"
                 :id="props.id">
        <!-- Título -->
        <PageSectionHeader title="*Contáctanos*"
                           subtitle="¡No dudes en escribirnos!"
                           :contrast="true"/>

        <!-- Contenido -->
        <PageSectionContent>
            <ArticleCustomContent class="p-0">
                <!-- Formulario de contacto -->
                <div class="contact-form-wrapper">
                    <ContactForm/>
                </div>

                <!-- Contact grid: box + map -->
                <div class="contact-grid">
                  <div class="contact-box">
                    <strong>Dirección</strong>
                    <p>Eusebio Lillo 362, Valparaíso</p>

                    <strong>Teléfono</strong>
                    <p>+56 9 8295 7538</p>

                    <strong>Email</strong>
                    <p>contacto@cirujanodesintetizadores.com</p>
                  </div>

                  <div class="map-frame">
                    <iframe
                      src="https://www.google.com/maps?q=Eusebio%20Lillo%20362,%20Valparaiso,%20Chile%20CP%202350454&output=embed"
                      loading="lazy"
                      referrerpolicy="no-referrer-when-downgrade">
                    </iframe>
                  </div>
                </div>

            </ArticleCustomContent>
        </PageSectionContent>
    </PageSection>
</template>

<script setup>
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionHeader from "/src/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"
import ArticleCustomContent from "/src/vue/components/articles/ArticleCustomContent.vue"
import ContactForm from "/src/vue/components/forms/contact/ContactForm.vue"

const props = defineProps({
    id: String
})
</script>
