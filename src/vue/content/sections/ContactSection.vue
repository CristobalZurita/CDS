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

<style lang="scss" scoped>
@use '@/scss/theming' as *;

.contact-form-wrapper {
  width: 100%;
  margin-bottom: 2rem;
}

.contact-grid {
  display: grid;
  grid-template-columns: minmax(280px, 420px) 1fr;
  gap: 32px;
  padding: 2rem 0;
  align-items: stretch;
}

@media (max-width: 768px) {
  .contact-grid {
    grid-template-columns: 1fr;
  }
}

.contact-box {
  border: 1px solid rgba($color-white, 0.06);
  padding: $spacer-xl 30px;
  border-radius: $border-radius-md;
  background: rgba($color-white, 0.03);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.contact-box strong {
  font-size: 1.35rem;
  font-weight: $fw-extrabold;
  color: $bg-paper;
}

.contact-box p {
  margin: 0;
  font-size: $text-xl;
  color: $light-2;
  line-height: $lh-relaxed;
}

.map-frame {
  width: 100%;
  min-height: 420px;
  border-radius: $border-radius-lg;
  overflow: hidden;
  border: 1px solid rgba($color-white, 0.08);
  box-shadow: 0 8px 24px rgba($color-black, 0.3);
}

.map-frame iframe {
  width: 100%;
  height: 420px;
  border: 0;
  display: block;
}
</style>
