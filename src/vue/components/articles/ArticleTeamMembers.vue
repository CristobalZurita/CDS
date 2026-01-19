<template>
    <article class="foxy-team-members row g-0">
        <div class="col-12">
            <div class="team-grid">
                <slot />
            </div>
        </div>
    </article>
</template>

<script setup>
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

.team-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 2rem;
    align-items: stretch;
}
</style>
