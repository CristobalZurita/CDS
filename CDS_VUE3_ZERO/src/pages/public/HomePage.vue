<template>
  <main class="home-page">
    <HeroSection />
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
  --layout-home-font-family-base: var(--layout-public-font-family-base);
  --layout-home-font-family-heading: var(--layout-public-font-family-heading);
  --layout-home-text-body: var(--layout-public-text-body);
  --layout-home-text-lead: clamp(calc(1.08rem * var(--cds-type-scale, 1)), calc((1rem + 0.5vw) * var(--cds-type-scale, 1)), calc(1.34rem * var(--cds-type-scale, 1)));
  --layout-home-text-title: clamp(calc(2.05rem * var(--cds-type-scale, 1)), calc((1.6rem + 2.25vw) * var(--cds-type-scale, 1)), calc(3.45rem * var(--cds-type-scale, 1)));
  --layout-home-text-card-title: clamp(calc(1.12rem * var(--cds-type-scale, 1)), calc((1.05rem + 0.38vw) * var(--cds-type-scale, 1)), calc(1.34rem * var(--cds-type-scale, 1)));
  --layout-home-text-card-body: clamp(calc(0.98rem * var(--cds-type-scale, 1)), calc((0.94rem + 0.22vw) * var(--cds-type-scale, 1)), calc(1.08rem * var(--cds-type-scale, 1)));
  --layout-home-text-meta: var(--layout-public-text-meta);
  --layout-home-card-padding: clamp(calc(1.18rem * var(--cds-type-scale, 1)), calc((1rem + 0.9vw) * var(--cds-type-scale, 1)), calc(1.62rem * var(--cds-type-scale, 1)));
  --layout-home-section-content-gap: clamp(calc(1.25rem * var(--cds-type-scale, 1)), calc((1rem + 2.5vw) * var(--cds-type-scale, 1)), calc(2rem * var(--cds-type-scale, 1)));
  color: var(--cds-text-normal);
  font-family: var(--layout-home-font-family-base);
}
</style>
