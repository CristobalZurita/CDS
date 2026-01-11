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
@import "@/scss/_theming.scss";

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
  border: 1px solid rgba(255,255,255,0.06);
  padding: 32px 30px;
  border-radius: 10px;
  background: rgba(255,255,255,0.03);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.contact-box strong {
  font-size: 1.35rem;
  font-weight: 800;
  color: #f5f5f5;
}

.contact-box p {
  margin: 0;
  font-size: 1.2rem;
  color: #e8e8e8;
  line-height: 1.6;
}

.map-frame {
  width: 100%;
  min-height: 420px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}

.map-frame iframe {
  width: 100%;
  height: 420px;
  border: 0;
  display: block;
}
</style>
