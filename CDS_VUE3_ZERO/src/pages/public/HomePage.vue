<template>
  <main class="home-page">
    <section id="hero" class="home-hero">
      <h1>{{ heroTitle }}</h1>
      <p>{{ heroSubtitle }}</p>

      <div class="hero-actions">
        <router-link
          v-for="action in primaryActions"
          :key="action.to"
          :to="action.to"
          class="hero-action"
          :class="`hero-action-${action.variant}`"
        >
          {{ action.label }}
        </router-link>
      </div>
    </section>

    <section class="home-nav">
      <h2>Navegación rápida</h2>
      <div class="home-nav-links">
        <a
          v-for="section in sections"
          :key="section.id"
          :href="`#${section.id}`"
          class="home-nav-link"
        >
          {{ section.name }}
        </a>
      </div>
    </section>

    <section
      v-for="section in contentSections"
      :id="section.id"
      :key="section.id"
      class="home-section"
    >
      <h3>{{ section.title }}</h3>
      <p>{{ section.description }}</p>
      <div class="section-links">
        <router-link
          v-for="link in section.links"
          :key="`${section.id}-${link.to}`"
          :to="link.to"
          class="section-link"
        >
          {{ link.label }}
        </router-link>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useHomePage } from '@new/composables/useHomePage'

const { heroTitle, heroSubtitle, primaryActions, sections, contentSections } = useHomePage()
</script>

<style scoped>
.home-page {
  padding: 1rem;
  display: grid;
  gap: 1rem;
}

.home-hero {
  padding: 1rem;
  border-radius: 1rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  background: var(--cds-white);
}

.home-hero h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
  line-height: var(--cds-leading-tight);
}

.home-hero p {
  margin: 0.4rem 0 0;
  font-size: var(--cds-text-base);
  line-height: var(--cds-leading-normal);
  color: var(--cds-text-muted);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.hero-action {
  min-height: 44px;
  padding: 0.7rem 1rem;
  border-radius: 0.6rem;
  text-decoration: none;
  font-size: var(--cds-text-base);
  display: inline-flex;
  align-items: center;
}

.hero-action-primary {
  background: var(--cds-primary);
  color: var(--cds-white);
  border: 1px solid var(--cds-primary);
}

.hero-action-secondary {
  color: var(--cds-primary);
  border: 1px solid color-mix(in srgb, var(--cds-primary) 45%, white);
}

.home-nav,
.home-section {
  padding: 1rem;
  border-radius: 1rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  background: var(--cds-white);
  scroll-margin-top: 5rem;
}

.home-nav h2,
.home-section h3 {
  margin: 0;
  font-size: var(--cds-text-xl);
}

.home-nav-links,
.section-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.home-nav-link,
.section-link {
  min-height: 44px;
  padding: 0.65rem 0.95rem;
  border-radius: 0.6rem;
  border: 1px solid color-mix(in srgb, var(--cds-primary) 25%, white);
  color: var(--cds-primary);
  text-decoration: none;
  font-size: var(--cds-text-base);
  display: inline-flex;
  align-items: center;
}

.home-section p {
  margin: 0.5rem 0 0;
  font-size: var(--cds-text-base);
  line-height: var(--cds-leading-normal);
}
</style>
