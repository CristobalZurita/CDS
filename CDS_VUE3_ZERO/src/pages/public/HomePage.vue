<template>
  <main class="home-page">
    <HeroSection />
    <AboutSection />
    <ServicesSection />
    <DiagnosticSection />
    <FeaturedSection />
    <FaqSection />
    <ReviewsSection />
    <ContactSection />
  </main>
</template>

<script setup>
import {
  HeroSection,
  AboutSection,
  ServicesSection,
  DiagnosticSection,
  FeaturedSection,
  FaqSection,
  ReviewsSection,
  ContactSection,
} from '@/components/home'
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
}
</style>
