<template>
    <PageWrapper id="foxy-home-page"
                 :no-padding="true"
                 :sections="sections"/>
</template>

<script setup>
import PageWrapper from "@/vue/components/layout/PageWrapper.vue"
import SectionInfo from '@/models/SectionInfo.js"
import AboutSection from "@/vue/content/sections/AboutSection.vue"
import ContactSection from "@/vue/content/sections/ContactSection.vue"
import FaqSection from "@/vue/content/sections/FaqSection.vue"
import FeaturedProjectSection from "@/vue/content/sections/FeaturedProjectSection.vue"
import HeroSection from "@/vue/content/sections/HeroSection.vue"
import ReviewsSection from "@/vue/content/sections/ReviewsSection.vue"
import ServicesSection from "@/vue/content/sections/ServicesSection.vue"
import DiagnosticSection from "@/vue/sections/DiagnosticSection.vue"  // ← AGREGAR

const sections = [
    new SectionInfo('hero',         HeroSection,            null,               null),
    new SectionInfo('about',        AboutSection,           'Nosotros',         'pi pi-box'),
    new SectionInfo('services',     ServicesSection,        'Servicios',        'pi pi-wrench'),
    new SectionInfo('diagnostic',   DiagnosticSection,      'Cotizar',          'pi pi-calculator'),
    new SectionInfo('featured',     FeaturedProjectSection, 'Disponible',       'pi pi-qrcode'),
    new SectionInfo('faq',          FaqSection,             'Preguntas',        'pi pi-question-circle'),
    new SectionInfo('reviews',      ReviewsSection,         'Opiniones',        'fa-regular fa-comment'),
    new SectionInfo('contact',      ContactSection,         'Contacto',         'fa-regular fa-envelope')
]
</script>

<style lang="scss" scoped>
</style>