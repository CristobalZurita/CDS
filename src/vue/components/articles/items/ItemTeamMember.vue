<template>
    <div class="team-card">
        <div class="team-image">
            <img 
                :src="image" 
                :alt="name"
                width="140"
                height="140"
                loading="lazy"
            />
        </div>

        <div class="team-body">
            <h3>{{ name }}</h3>
            <p>{{ role }}</p>

            <div v-if="links && links.length" class="team-links">
                <a v-for="(link, index) in links"
                   :key="index"
                   :href="link.href"
                   target="_blank"
                   rel="noopener noreferrer">
                    <i :class="link.faIcon" />
                </a>
            </div>
        </div>
    </div>
</template>

<script setup>
defineProps({
    name: { type: String, required: true },
    role: { type: String, required: true },
    image: { type: String, required: true },
    links: { type: Array, default: () => [] },
})
</script>

<style lang="scss" scoped>
@use '@/scss/theming' as *;

.team-card {
    background: $vintage-beige;
    border-radius: $border-radius-xl;
    border: 1px solid rgba($color-dark, 0.16);
    box-shadow: 0 12px 24px rgba($color-dark, 0.15);
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: $spacer-lg 1.25rem 1.75rem;
    gap: $spacer-md;
}

.team-image {
    width: 140px;
    height: 140px;
    border-radius: $border-radius-xl;
    overflow: hidden;
    border: 2px solid rgba($color-primary, 0.5);
    background: $light-2;
}

.team-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.team-body h3 {
    margin: 0;
    font-size: 1.4rem;
    color: $brand-text;
    font-family: $headings-font-family;
}

.team-body p {
    margin: 0.35rem 0 0.75rem;
    color: $text-normal;
    font-weight: $fw-semibold;
}

.team-links {
    display: flex;
    gap: 0.75rem;
    justify-content: center;
}

.team-links a {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 1px solid rgba($color-dark, 0.2);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: $orange-pastel;
    background: rgba($color-primary, 0.08);
    transition: $transition-fast;
}

.team-links a:hover {
    background: rgba($color-primary, 0.2);
    border-color: rgba($color-primary, 0.5);
    color: $brand-text;
}
</style>
