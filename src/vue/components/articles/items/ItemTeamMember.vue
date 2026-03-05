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
